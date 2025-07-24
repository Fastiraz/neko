---
sidebar_position: 1
title: Agent
description: How to configure the autonomous agent.
---

# Agent Configuration

The Neko agent relies on several models and services, which can be configured using a `.env` file at the project root or wherever your backend is initialized.

This file allows you to customize which models are used, where local data is stored, and how the agent behaves.

---

## Example `.env` File

```dotenv
# === Models ===
MODEL="qwen3:14b"
EMBED_MODEL="mxbai-embed-large:latest"
VISION_MODEL="llama3.2-vision:latest"
BROWSER_MODEL="llama3.1:8b"
BROWSER_PLANNER_MODEL="deepseek-r1:14b"

# === Browser Use ===
OLLAMA_HOST=http://localhost:11434
BROWSER_USE_LOGGING_LEVEL=info
ANONYMIZED_TELEMETRY=false

# === Paths ===
VECTOR_DB_PATH=/home/user/neko/backend/vectordb
DATASETS_PATH=/home/user/neko/backend/datasets
````

---

## Configuration Sections

### Models

- `MODEL`: LLM used for reasoning.
- `EMBED_MODEL`: Embedding model used for vector similarity (RAG).
- `VISION_MODEL`: Multimodal model used for interpreting images.
- `BROWSER_MODEL`: Model used for web browsing and tool-assisted tasks.
- `BROWSER_PLANNER_MODEL`: Model used to plan multistep browser actions.

### Browser & LLM Server

- `OLLAMA_HOST`: Where your Ollama or LLM server is running (e.g. `http://localhost:11434`).
- `ANONYMIZED_TELEMETRY`: Disable sending any anonymous usage metrics.

### Paths

- `VECTOR_DB_PATH`: Local path to the vector database.
- `DATASETS_PATH`: Path to raw or processed datasets used by the agent.
