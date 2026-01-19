# mcpl-antigravity

This repository serves as a unified workspace for **n8n workflow automation** and **MCP (Model Context Protocol)** tooling. It aggregates the core components required to build, test, and deploy intelligent workflows using AI agents.

## 📂 Repository Structure

*   **`mcp-launchpad-debug/`**: The CLI (`mcpl`) orchestrator that connects AI models (like Claude/Gemini) to your local tools.
*   **`n8n-mcp/`**: A Model Context Protocol server that bridges n8n with AI, exposing nodes and documentation as tools.
*   **`n8n-skills/`**: A collection of "skills" (guides/prompts) that teach AI agents how to use `n8n-mcp` effectively.

## 🚀 Getting Started

### 1. Prerequisites
*   Node.js (v18+)
*   Python (3.13+)
*   `uv` (for Python management)

### 2. Configuration (`mcp.json`)
A unified `mcp.json` is provided in the root. This configures `mcpl` to use the local `n8n-mcp` server.

### 3. Usage

#### Using the Launchpad (`mcpl`)
This is your primary entry point for AI tools.

```bash
cd mcp-launchpad-debug
# Run the launchpad (ensure dependencies are installed)
uv run mcpl search "n8n"
```

#### n8n Skills
To enable the AI skills for n8n, you can install the `n8n-skills` manually or via plugin commands found in `n8n-skills/README.md`.

## 🛠 Maintenance

*   **n8n-mcp**: If you modify the source, rebuild it:
    ```bash
    cd n8n-mcp
    npm install
    npm run build
    ```

## 🔐 Credentials
Ensure you have a `.env` file in the root (or specific subprojects) with:
*   `GOOGLE_API_KEY`
*   `OPENROUTER_API_KEY`
*   `N8N_API_KEY` (if controlling a live n8n instance)

---
*Created by Antigravity*
