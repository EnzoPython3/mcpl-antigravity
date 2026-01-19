# CLAUDE.md

This file provides guidance to Claude/Antigravity when working with code in this workspace.

## Repository Overview

This is a consolidated workspace focused on **n8n workflow automation** and **MCP (Model Context Protocol)** integration. The primary project is **`mcpl-antigravity`**, which aggregates core tooling.

## Workspace Structure

### Core Repository: mcpl-antigravity/
- **`mcp-launchpad-debug/`**: CLI orchestrator for MCP servers.
- **`n8n-mcp/`**: MCP server bridging n8n documentation and tools to AI.
- **`n8n-skills/`**: Best practices and skill definitions for n8n development.

### Global Skills: .agent/skills/
- **`creating-skills/`**: A system meta-skill for generating new Antigravity skills. Always reference this when tasked with building a new skill.

## Development Principles

- **Local-First**: Prioritize tools and logic that leverage the M3 Pro MacBook's capabilities.
- **n8n Focus**: Workflows should be modular, validated, and follow the structures defined in `n8n-skills`.
- **MCP Integration**: Use `mcpl` from `mcp-launchpad-debug` to interact with tools.

## Key Files
- `mcpl-antigravity/README.md`: Detailed architecture and setup for the core stack.
- `mcpl-antigravity/mcp.json`: Local MCP server configuration.

---
*Maintained by Antigravity*
