# 🔒 Ma'at: Privacy Policy & ToS Analyzer

This project is a legal-focused RAG system (named **Ma'at**) that processes and analyzes privacy policies and Terms of Service (ToS) documents. It utilizes **Hypothetical Document Embeddings (HyDE)** for precise retrieval of dense legal clauses and implements a **ReAct Agent** equipped with custom MCP tools (Date Calculator, Legal Dictionary) to translate complex legal terms into simple answers.

## Project Structure

```
privacy-analyzer/
├── README.md                 # Setup instructions and overview
├── .env                      # API keys (OpenRouter configuration)
├── chroma_db/                # Local vector database (auto-generated)
├── data/                     # 33 raw markdown legal policies
├── rag/
│   ├── indexing.py           # Document processing and embedding into ChromaDB
│   └── retrieval.py          # RAG retrieval and HyDE query formulation
├── mcp_server/
│   └── server.py             # FastMCP server with tools and CCPA resource
├── evaluation/
│   ├── test_queries.json     # 10 test evaluation questions
│   └── results.md            # Evaluation results & failure cases
├── examples/
│   └── demo.py               # ReAct Agent and Jinja2 template integration
└── scripts/
    └── download_data.py      # Automated download script for CITP dataset
```

## Setup & Configuration

1. **Install Dependencies**:
   This project uses `uv` for python dependency management and uses the parent virtual environment. Make sure the dependencies are installed:
   ```bash
   uv add langchain langchain-chroma langchain-openai langchain-huggingface chromadb fastmcp python-dotenv sentence-transformers jinja2 mcp langchain-community
   ```

2. **Configure API Keys**:
   Create a `.env` file inside the `privacy-analyzer/` folder:
   ```env
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   OPENROUTER_API_BASE="https://openrouter.ai/api/v1"
   OPENROUTER_MODEL="openrouter/owl-alpha"
   ```

## How to Run

### 1. Document Indexing (RAG Setup)
To build/refresh the local ChromaDB vector store:
```bash
uv run python privacy-analyzer/rag/indexing.py
```

### 2. Run the MCP Server
To start the FastMCP Server in development mode with the **MCP Inspector** web UI:
```bash
uv run fastmcp dev inspector privacy-analyzer/mcp_server/server.py:mcp
```
*(This starts the server and provides an inspector UI link to inspect the tools and resources).*

Alternatively, to run the server in standard stdio mode:
```bash
uv run fastmcp run privacy-analyzer/mcp_server/server.py:mcp
```

### 3. Run the ReAct Agent Demo
To test the agent flow on sample queries:
```bash
uv run python privacy-analyzer/examples/demo.py
```
This script will query the local vector store using HyDE and execute tools (`calculate_data_retention` and `define_legal_term`) natively using LLM tool calling.
