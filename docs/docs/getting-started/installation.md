---
sidebar_position: 3
title: Installation
description: How to install and run the Neko platform using Docker or from source
---

# Installation

Neko is built using various technologies, but everything is **containerized** for ease of deployment. You can choose between a **container-based setup (recommended)** or install from source if you want full control.

---

## 🚀 Installation with Containers (Recommended)

The fastest way to get started is with Docker.

### Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Start All Services

From the project root:

```sh
docker-compose up
````

This command launches all major components defined in `compose.yaml`, including:

* Backend (API, MCP, autonomous agents, vector DB, knowledge base)
* Frontend (ReactApp for UI)
* PocketBase (auth/db)
* ComfyUI (visual/AI tools)
* Hacking environment
* Ollama (LLM provider)

> 💡 Modify the `*.dockerfile` files to customize each service.

Once running, check the default URLs (typically `http://localhost:3000`, `http://localhost:8000`, etc. based on your `compose.yaml`).

---

## 🧩 Installation from Source (Advanced)

Use this method if you want to run everything directly without containers.

### Step 1: Install System Dependencies

You'll need:

- **[Python 3.12+](https://www.python.org/)**
- **[uv](https://github.com/astral-sh/uv)**: An extremely fast Python package, environment and project manager, written in Rust.
- **[bun](https://bun.sh/)**: Bun is a fast JavaScript
all-in-one.
- **[Ollama](https://ollama.com/)**: An LLM provider.
- **[Docker](https://www.docker.com/)**: A container manager.
- **[ComfyUI](https://www.comfy.org/)**: A powerful open source node-based
application for generative AI.
- **[PocketBase](https://pocketbase.io/)**: A Backend as a Service.

---

<div align="center">
  <code>Coming soon...</code>
</div>
