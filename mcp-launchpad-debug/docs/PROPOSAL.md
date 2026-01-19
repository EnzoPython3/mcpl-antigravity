# MCP Launchpad - Design Proposal

## Problem Statement

When connecting multiple MCP servers to Claude Code, the tool definitions consume a significant portion of the context window before any work begins. As documented by Anthropic:

- **GitHub**: 35 tools (~26K tokens)
- **Slack**: 11 tools (~21K tokens)  
- **Sentry**: 5 tools (~3K tokens)
- **Grafana**: 5 tools (~3K tokens)

A modest 5-server setup consumes **~55K tokens** just for tool definitions. At Anthropic, they've seen tool definitions consume **134K tokens** before optimization.

This creates two problems:
1. **Context bloat**: Less room for actual conversation and code
2. **Tool selection errors**: Similar tool names cause confusion (e.g., `notification-send-user` vs `notification-send-channel`)

## Solution: MCP Launchpad

A lightweight CLI tool that acts as a **tool discovery and execution gateway** for MCP servers. Instead of Claude Code connecting directly to all MCP servers (loading all tools), Claude Code uses mcp-launchpad to:

1. **Search** for relevant tools using BM25/regex matching
2. **Inspect** specific tool definitions on-demand  
3. **Execute** tools with precise parameters

This mirrors Anthropic's "Tool Search Tool" pattern but implemented as an external CLI that Claude Code can invoke.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude Code                             │
│  (Only knows about mcp-launchpad CLI - minimal context cost)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      mcp-launchpad CLI                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ Tool Search │  │ Tool Inspect │  │ Tool Execute          │  │
│  │ (BM25/Regex)│  │ (On-demand)  │  │ (JSON in/out)         │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐    ┌──────────┐
        │ MCP      │   │ MCP      │    │ MCP      │
        │ Server 1 │   │ Server 2 │    │ Server N │
        └──────────┘   └──────────┘    └──────────┘
```

## Core Commands

> **Note:** The CLI is available as both `mcp-launchpad` and `mcpl` (short alias).

### 1. `mcpl search <query>` - Find relevant tools
```bash
# Human-friendly output (default)
$ mcpl search "github pull request"
Found 3 tools matching "github pull request":

[github] create_pull_request
  Create a new pull request in a repository

[github] list_pull_requests  
  List pull requests with optional filters

[github] merge_pull_request
  Merge an existing pull request

# JSON output for Claude Code (--json flag goes before command)
$ mcpl --json search "github pull request"
{
  "query": "github pull request",
  "method": "bm25",
  "results": [
    {"server": "github", "tool": "create_pull_request", "score": 0.89, "description": "..."},
    {"server": "github", "tool": "list_pull_requests", "score": 0.85, "description": "..."}
  ]
}
```

**Search Methods** (inspired by Anthropic's approach):
- `--method bm25` (default): BM25 ranking for natural language queries
- `--method regex`: Regex pattern matching on tool names/descriptions
- `--method exact`: Exact substring match

### 2. `mcpl inspect <server> <tool>` - Get full tool definition
```bash
$ mcpl --json inspect github create_pull_request
{
  "server": "github",
  "tool": "create_pull_request", 
  "description": "Create a new pull request...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "owner": {"type": "string", "description": "Repository owner"},
      "repo": {"type": "string", "description": "Repository name"},
      "title": {"type": "string", "description": "PR title"},
      "body": {"type": "string", "description": "PR description"},
      "head": {"type": "string", "description": "Branch containing changes"},
      "base": {"type": "string", "description": "Branch to merge into"}
    },
    "required": ["owner", "repo", "title", "head", "base"]
  }
}
```

### 3. `mcpl call <server> <tool> [args]` - Execute a tool
```bash
# With inline JSON args
$ mcpl --json call github create_pull_request '{"owner": "acme", "repo": "api", "title": "Fix bug", "head": "fix-123", "base": "main"}'

# With args from stdin (for large payloads)
$ echo '{"owner": "acme", ...}' | mcpl --json call github create_pull_request --stdin

# Output
{
  "success": true,
  "result": {
    "number": 42,
    "url": "https://github.com/acme/api/pull/42",
    "state": "open"
  }
}
```

### 4. `mcpl list` - List all servers and tools
```bash
$ mcpl --json list
{
  "servers": [
    {"name": "github", "status": "connected", "tools": 35},
    {"name": "slack", "status": "connected", "tools": 11},
    {"name": "sentry", "status": "error", "error": "Connection refused"}
  ]
}

$ mcpl --json list github  # List tools for specific server
{
  "server": "github",
  "tools": [
    {"name": "create_pull_request", "description": "..."},
    {"name": "list_issues", "description": "..."}
  ]
}
```

## Config File Discovery

The CLI will automatically discover MCP server configurations in this order (first found wins):

1. **Project-level**: `./.mcp.json` or `./.claude/mcp.json`
2. **User-level**: `~/.claude/mcp.json`
3. **Explicit**: `--config <path>` flag

Similarly for environment variables:

1. **Project-level**: `./.env`
2. **User-level**: `~/.claude/.env`
3. **Explicit**: `--env-file <path>` flag

### Config Format (Standard MCP Format)

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": {
        "SLACK_TOKEN": "${SLACK_TOKEN}"
      }
    }
  }
}
```

## Installation & Distribution

As a **uv tool**, users can install directly from GitHub:

```bash
# Install globally
uv tool install git+https://github.com/yourusername/mcp-launchpad

# Or run without installing
uvx git+https://github.com/yourusername/mcp-launchpad search "github issues"
```

## Context Savings Analysis

### Before (Direct MCP Connection)
Claude Code connects to 5 MCP servers:
- Tool definitions: **~55,000 tokens**
- Available for conversation: Reduced

### After (Using mcp-launchpad)
Claude Code knows one CLI interface:
- mcp-launchpad usage: **~500 tokens** (in system prompt or memory)
- Per-search overhead: **~100-300 tokens** (search results)
- Per-tool inspection: **~200-500 tokens** (only when needed)
- **95%+ token savings** on tool definitions

## Technical Implementation

### Dependencies
- `mcp` - Official MCP SDK for Python
- `click` - CLI framework
- `rank-bm25` - BM25 search implementation
- `python-dotenv` - Environment variable loading

### Key Components

```
mcp_launchpad/
├── __init__.py
├── cli.py              # Click CLI entry point
├── config.py           # Config discovery & loading
├── connection.py       # MCP server connection management
├── search.py           # BM25 and regex search implementations
└── output.py           # JSON/human-readable formatters
```

### Connection Management

MCP servers are connected **lazily per-server** - only when that server's tools are needed:

```bash
$ mcp search "github"           # Uses cached tool index, no connections yet
$ mcp call github list_issues   # NOW connects to github server
$ mcp call slack send_message   # NOW connects to slack server
```

**Timeouts**: 30 seconds for both server connections and tool calls.

### Tool Index Caching

To enable fast searching without connecting to all servers, we cache the tool index:

```
~/.cache/mcp-launchpad/
├── tool_index.json          # Cached tool definitions from all servers
└── index_metadata.json      # Last update timestamps per server
```

The cache is rebuilt when:
- `mcp list --refresh` is called
- Config file changes (detected via mtime)
- Cache is older than configurable TTL (default: 24 hours)

### Error Handling

Errors must be **actionable** since this tool is primarily used by AI agents. Every error includes:
1. **Traceback** for debugging
2. **Helpful explanation** of what went wrong
3. **Actionable fix** for common issues

```json
{
  "success": false,
  "error": {
    "type": "ServerConnectionError",
    "message": "Failed to connect to 'github' server",
    "traceback": "...",
    "help": "The github server requires GITHUB_TOKEN to be set. Add it to your .env file:\n\nGITHUB_TOKEN=ghp_your_token_here\n\nYou can create a token at: https://github.com/settings/tokens"
  }
}
```

Common helpful error patterns:
- Missing API keys → Explain which key, where to set it, how to get one
- Server not found → List available servers, suggest similar names
- Tool not found → Suggest `mcp search` to find the right tool
- Invalid arguments → Show the expected schema with examples
- Timeout → Suggest increasing timeout or checking server health

## Claude Code Integration

Claude Code can use mcp-launchpad through its existing CLI tool capabilities. A suggested system prompt addition:

```
You have access to MCP tools through the `mcpl` CLI (mcp-launchpad).
Instead of having all tools loaded, use these commands to discover and execute tools:

- `mcpl --json search "<query>"` - Find tools matching your needs
- `mcpl --json inspect <server> <tool>` - Get full tool schema before calling
- `mcpl --json call <server> <tool> '<json-args>'` - Execute a tool
- `mcpl --json list` - See all available servers and tools

Always search first, inspect the schema, then call with correct parameters.
```

## Future Enhancements (Out of Scope for v1)

1. **Daemon mode**: Persistent connections across invocations
2. **Tool caching**: Cache tool definitions locally for faster search
3. **Embedding search**: Semantic search using embeddings (like Anthropic suggests)
4. **Server health monitoring**: Track connection status and auto-reconnect
5. **Batch operations**: Execute multiple tool calls in one invocation
6. **Interactive mode**: REPL for exploration (lower priority per requirements)

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Connection lifecycle | Lazy per-server | Only connect when needed, reduces startup time |
| Search indexing | Cached | Fast search without connecting to all servers |
| Error handling | Traceback + helpful messages | AI agents need actionable guidance |
| Timeouts | 30 seconds | Reasonable for most MCP server operations |

## Next Steps

1. Review and refine this proposal
2. Set up project structure with uv
3. Implement config discovery
4. Implement MCP server connections
5. Implement search (BM25 + regex)
6. Implement CLI commands
7. Add tests
8. Documentation and README

