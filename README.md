# Personal OS: Agentic LangGraph Assistant

A sophisticated, autonomous personal assistant framework built with **LangGraph**, **Gemini 2.5 Flash**, and **Model Context Protocol (MCP)**. This assistant doesn't just chat—it manages your academic life, drafts your emails, and remembers your past activities using a persistent vector memory layer.

## Overview
Personal OS is designed to be a "proactive" agent. It aggregates data from multiple silos (Canvas, Gmail, Calendar), reasons about priorities using an agentic workflow, and takes autonomous actions via tool-calling.

### Key Features:
*   **Agentic Workflow:** Uses LangGraph to orchestrate specialized agents (Triage, Academic, Communications, Synthesis).
*   **Long-Term Memory:** Integrated **ChromaDB** vector store using semantic embeddings to remember past context across runs.
*   **Real-World Actions:** Autonomous tool-calling for drafting Gmail replies and scheduling Google Calendar events.
*   **MCP Integration:** Built on the Model Context Protocol for modular, extensible tool management.

---

## The Agent Graph
The assistant operates as a stateful graph:

1.  **Triage Node:** Fetches live data from APIs and retrieves relevant semantic memories from ChromaDB.
2.  **Academic Agent:** Analyzes Canvas deadlines and schedules study blocks via Google Calendar.
3.  **Communications Agent:** Scans for urgent emails and uses the `create_draft` tool to prepare replies.
4.  **Synthesis Agent:** Compiles all actions and insights into a formatted "Daily Report."
5.  **Tool Node:** Executes the actual Python logic for any tools (Gmail/Calendar) the agents decide to call.

---

## Model Context Protocols (MCPs)
The project utilizes the following MCP servers (locally integrated):
*   **GSuite MCP:** Handles Gmail (list, read, draft) and Google Calendar (list, add).
*   **Canvas MCP:** Connects to the Canvas LMS API to fetch to-do items and upcoming events.

---

## Setup & Installation

### Prerequisites:
*   [uv](https://github.com/astral-sh/uv) installed for fast Python package management.
*   Google Cloud Project with Gmail and Calendar APIs enabled.
*   Canvas API Token.

### 1. Clone & Install
```bash
git clone <your-repo-url>
cd personal-os
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
CANVAS_BASE_URL=your_base_canvas_key
CANVAS_API_TOKEN=your_canvas_token
```

### 3. Google API Credentials
Place your `credentials.json` from the Google Cloud Console in the root directory. On the first run, the assistant will open a browser for OAuth2 authentication and generate `token_primary.json`.

---

## Usage
Run the assistant from the project root using the module flag:

```bash
uv run python -m graph.main
```

---

## Tech Stack
*   **Framework:** LangGraph
*   **LLM:** Gemini 2.5 Flash
*   **Database:** ChromaDB (Vector Store)
*   **Integrations:** Google Workspace APIs, Canvas LMS API
*   **Environment:** uv + python-dotenv
