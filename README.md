# mcpl-antigravity

This repository serves as a unified workspace for **n8n workflow automation** and **MCP (Model Context Protocol)** tooling. It aggregates the core components required to build, test, and deploy intelligent workflows using AI agents.

## 📂 Repository Structure

*   **`mcp-launchpad-debug/`**: The CLI (`mcpl`) orchestrator that connects AI models (like Claude/Gemini) to your local tools.
*   **`n8n-mcp/`**: A Model Context Protocol server that bridges n8n with AI, exposing nodes and documentation as tools.
*   **`n8n-skills/`**: A collection of "skills" (guides/prompts) that teach AI agents how to use `n8n-mcp` effectively.
*   **`workflow_factory_cli/`**: A specialized dual-agent (Planner/Executor) system for generating n8n workflows from natural language.

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

#### Using Workflow Factory
Generate workflows automatically.

```bash
cd workflow_factory_cli
# Activate venv and run
source .venv/bin/activate
python main.py "Create a workflow that..."
```

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
