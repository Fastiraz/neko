<div align="center">
  <img src="assets/logo.png" width="250">
</div>

<div align="center">
  <h1><code>akio</code></h1>
  <p>Your red team assistant who helps you break things.</p>
</div>

---

> [!WARNING]
> **Akio is under active development.**
> The project is not yet fully functional and may not work as expected out of the box.
> If you'd like to contribute, feel free to open a [pull request](https://github.com/Fastiraz/akio/pulls).
> Found a bug, vulnerability, or something unusual? Please open an [issue](https://github.com/Fastiraz/akio/issues).

---

## What is Akio?

Akio is an autonomous AI agent specialized in offensive security. It combines the power of a large language model (LLM) with real-world capabilities by integrating with a shell, a web browser, a Retrieval-Augmented Generation (RAG) pipeline, and popular tools like **Ghidra** and **Burp Suite** through an MCP server.

**It's not build to replace** penetration testers, Akio is designed to **assist** them helping automate tasks, accelerate workflows, and provide intelligent interaction with common red team tools.

---

## Features

- Uncensored LLM
- Autonomous AI agent
- Tools
- - Shell commands execution
- - RAG for offensive security topics
- - Browser use
- - Message interaction with user
- - Web search (DuckDuckGo)
- - Coding agent

---

## The Grimoire

The Grimoire is the official Akio's documentation.
You can read it [here](https://fastiraz.github.io/grimoire/).

---

## Installation

You can read the installation instructions in the [Grimoire](https://fastiraz.github.io/grimoire/docs/getting-started/installation).

### Using pipx (recommend)

```sh
pipx install akio
```

### From source

```sh
git clone https://github.com/Fastiraz/akio.git
cd akio

uv build
uv venv
uv pip install dist/*.whl
uv run -- akio
```

---

<div align="center">
  <p><code>Coming soon...</code></p>
</div>
