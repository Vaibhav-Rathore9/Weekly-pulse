# Weekly Product Review Pulse - System Architecture

This document defines the high-level architecture and component design for the Weekly Product Review Pulse AI Agent. This system is an LLM-driven agent that ingests reviews from the App Store and Google Play, processes them to generate actionable insights, and autonomously decides to deliver a consolidated report via Google Docs and Gmail using tools provided by the Model Context Protocol (MCP).

## 1. System Overview

The system is designed around an autonomous AI Agent framework (e.g., LangChain/LangGraph or similar, Python-based). The core LLM orchestrates the workflow and acts as an MCP client equipped with tools from an external MCP server (`saksham-mcp-server`) responsible for interacting with Google Workspace APIs.

### High-Level Data Flow

1. **Trigger**: A scheduled cron job or CLI command initiates a run for a specific Product and ISO Week.
2. **Ingestion**: The agent scrapes Google Play and fetches the iTunes RSS feed to gather public reviews from the last 8-12 weeks.
3. **Processing**: Reviews are scrubbed for PII, embedded into vector representations, clustered to identify themes, and passed to an LLM.
4. **Reasoning**: The LLM extracts themes, validates representative quotes, and suggests action items.
5. **Rendering**: The structured LLM output is compiled into Markdown (for Docs) and HTML/Text (for Email).
6. **Delivery via MCP**: The AI Agent connects to the remote MCP server (`saksham-mcp-server`) and autonomously uses MCP tools to append the report to a Google Doc and send an email to stakeholders.

## 2. Component Design

The system is organized into five core modules.

### 2.1 AI Agent Orchestrator
- **Role**: An LLM-driven core that coordinates the workflow, reasons about tasks, uses available tools, and manages system state.
- **Components**:
  - **Job Scheduler**: Entry point (e.g., standard cron or GitHub Actions).
  - **CLI**: Allows triggering manual backfills for specific ISO weeks.
  - **State & Idempotency Manager**: Uses a local SQLite database (`pulse_state.db`) to track successful runs. Before executing, it checks if `(Product, ISO_Week)` has already been successfully delivered.

### 2.2 Ingestion Module
- **Role**: Fetches raw data from external storefronts.
- **Components**:
  - **App Store Fetcher**: Parses the iTunes RSS feed (e.g., using `feedparser` or raw HTTP requests).
  - **Google Play Fetcher**: Scrapes Google Play using libraries like `google-play-scraper`.
  - **Normalizer**: Converts raw reviews into a unified schema: `[ReviewID, Date, Source, Rating, Text, AppVersion]`.

### 2.3 Processing & Reasoning Module (The Brain)
- **Role**: Analyzes the raw text to produce meaningful insights.
- **Components**:
  - **PII Scrubber**: A regex/NER step that redacts phone numbers, emails, and names from the review text before processing.
  - **Embedder**: Generates vector embeddings for the scrubbed reviews (e.g., using OpenAI's `text-embedding-3-small` or HuggingFace local models).
  - **Clusterer**: Uses **UMAP** for dimensionality reduction and **HDBSCAN** for density-based clustering to group similar reviews automatically.
  - **LLM Engine**: Prompts an LLM (e.g., GPT-4o, Claude, or Gemini) for each cluster to:
    - Name the theme.
    - Extract representative quotes.
    - Suggest an action idea.
  - **Quote Validator**: Ensures that quotes returned by the LLM are literal substrings of actual reviews in the cluster to prevent hallucination.

### 2.4 Rendering Module
- **Role**: Formats the extracted insights into the desired output format.
- **Components**:
  - **Docs Renderer**: Generates the final Markdown format matching the "One-page narrative" requirement.
  - **Email Renderer**: Generates a brief teaser email containing top themes as bullet points and a deep link to the newly appended Google Doc section.

### 2.5 Delivery via Agent Tool-Use (MCP Client)
- **Role**: The AI agent autonomously uses provided tools to send the rendered output to the external MCP server.
- **Components**:
  - **MCP Client**: Implements the Model Context Protocol to fetch available tools from the `saksham-mcp-server`.
  - **Docs Appender Tool**: An MCP tool provided to the AI agent. The agent invokes it to find the canonical Google Doc and append the new section.
  - **Gmail Sender Tool**: An MCP tool provided to the AI agent. The agent invokes it to draft and send the stakeholder email.

## 3. Technology Stack

- **Core Language**: Python 3.10+
- **Data & AI Processing**:
  - `pandas`: Data manipulation and normalization.
  - `umap-learn` & `hdbscan`: Clustering.
  - `langchain` / `litellm`: LLM and embedding orchestration.
- **Ingestion**:
  - `google-play-scraper`: For Google Play reviews.
  - `requests`: For iTunes RSS.
- **Database**: `sqlite3` (built-in) for idempotency and state tracking.
- **MCP Delivery**: Python MCP SDK (`mcp` package) to interface with the external server over HTTP/SSE or stdio depending on the server's transport.

## 4. Data Security and Privacy
- **OAuth / Secrets**: The agent **does not** handle Google OAuth credentials. All Google interactions are delegated to the `saksham-mcp-server`. The agent only stores the API keys required for LLM/Embeddings.
- **PII Scrubbing**: Reviews are treated as data and scrubbed before leaving the execution environment to ensure compliance.
