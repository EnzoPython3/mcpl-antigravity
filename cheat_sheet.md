# ⚡ mcpl-antigravity: Cheat Sheet

## 🛠 Core Tools
| Tool | command | Purpose |
| :--- | :--- | :--- |
| **Launchpad** | `mcpl` | Run MCP-connected tools via CLI |
| **Workflow CLI** | `wfcli` | (Optional) Generate n8n via Python agents |
| **n8n Server** | `n8n-mcp` | Knowledge base & validation server |

## 🤖 The Workflow
1.  **Plan (Gemini):** "Let's plan a [Goal] workflow using the `automating-n8n-workflows` patterns."
2.  **Build (Claude):** "Implement the n8n JSON. Use `managing-brand-identity` for styling and `n8n-skills` for syntax."
3.  **Validate:** "Run `validate_workflow` on this JSON."
4.  **Harden:** "Apply Tier 2 hardening (logging and status codes)."

## 💡 Quick Prompts
- **"Search nodes for [Service]"** → Find available n8n integrations.
- **"Get docs for [Node Name]"** → Read official node documentation.
- **"Fix my expression: {{ $json.field }}"** → Debug data mapping errors.
- **"Apply brand identity"** → Ensure UI/Design tokens match brand rules.

## 🔐 Credentials Checklist
- [ ] `.env` loaded with API keys?
- [ ] `N8N_API_KEY` configured?
- [ ] Using Credentials storage instead of hardcoding?

---
*Created by Antigravity*
