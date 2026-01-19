---
name: automating-n8n-workflows
description: Expert guide for building, validating, and managing production-ready n8n workflows using MCP tools. Use when planning architectural patterns with Gemini or implementing precise JSON mappings with Claude.
---

# n8n Automation Expert

This skill consolidates documentation for building high-quality n8n workflows using the Model Context Protocol (MCP).

## When to use this skill
- Planning workflow architecture (Gemini).
- Creating or editing n8n JSON (Claude).
- Troubleshooting expression errors or validation failures.
- Hardening workflows for production readiness.

## Workflow

### 1. Pattern Selection
Identify the architectural blueprint:
- **Webhook Processing**: Incoming data security.
- **HTTP API Integration**: External service connection.
- **Database Operations**: Safe read/write sequences.
- **AI Agent Workflows**: LLM & Tool integration.
- **Scheduled Tasks**: Cron-job automation.

### 2. Implementation Rules
- **Expressions**: Use `{{ }}`. Access webhook data via `$json.body`.
- **Variables**: Use `$json`, `$node`, `$now`, `$env`.
- **Node Config**: Use `get_node_essentials` to save context window space.
- **JavaScript**: Preferred for 95% of logic cases. Use `$input` and `$json`.
- **Python**: Standard library ONLY. No `pandas` or `requests`.

### 3. Hardening (Production Readiness)
- **Tier 1 (Prototype)**: Basic null checks, simple try-catch.
- **Tier 2 (Production)**: Full input validation, external logging, HTTP status codes.
- **Tier 3 (Compliance)**: Idempotency, rate limiting, rollback strategies.

## Instructions

### Tool Usage
- `search_nodes`: Semantic search for functionality.
- `get_node_info`: Detailed schemas and properties.
- `validate_workflow`: **MANDATORY** before considering a task complete.
- `n8n_update_workflow`: Supports partial updates.

### Best Practices
- **Validation First**: Always run `validate_workflow`.
- **No Hardcoding**: Use n8n Credentials storage, not plain text.
- **Hallucination Check**: Manually review node connections and property mappings.
- **Prompting**: Be specific (e.g., "Build a webhook to Slack workflow with form validation").

## Resources
- [Full Documentation](resources/best-practices.md)
- [n8n MCP Tools Guide](https://github.com/czlonkowski/n8n-mcp)
