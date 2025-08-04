---
sidebar_position: 1
title: Roadmap
description: Roadmap
---

# Roadmap

Our product roadmap is where you can learn about what features we're working on, what stage they're in, and when we expect to bring them to you. Have any questions or comments about items on the roadmap? Share your feedback via our [Discord](https://discord.com).

The roadmap repository is for communicating GitHub’s roadmap. Existing issues are currently read-only, and we are locking conversations, as we get started. Interaction limits are also in place to ensure issues originate from GitHub. We’re planning to iterate on the format of the roadmap itself, and we see potential to engage more in discussions about the future of GitHub products and features. If you have feedback about this roadmap repository itself, such as how the issues are presented, let us know through [Discord](https://discord.com).

## Features

### Shipped features

The following is a list of shipped features:

- [x] Uncensored LLM
- [x] Autonomous AI agent
- [x] Tools
  - [x] Shell commands execution
  - [x] RAG for offensive security topics
  - [x] Browser use
  - [x] Message interaction with user
  - [x] Web search (DuckDuckGo)
  - [x] Coding agent

### Coming features

The following is a list of features we're working on:

- [ ] **agentic coding:** Enable the AI agent to code exploits
- [ ] **images/videos:** Enable the AI gent to generate images and videos (will be resource-intensive and may significantly impact performance)
- [ ] **react app:** A web-based user interface for interacting with the platform
  - [ ] **voice input/output:** Enable voice-based interaction with the LLM
  - [ ] **browser live view:** Displays agent activity and task execution in real time
  - [ ] **image input/output:** Allows uploading images as input and viewing generated visual output
  - [ ] **File upload:** Allows uploading files
- [ ] **MCP:** Use Model Context Protocol for tooling so we can use GUI apps
- [ ] **GEOINT:** Use Overpass Turbo and/or Plonk to geolocate an image
- [ ] **Context summarizer:** Save space in context
- [ ] Smart memory management
- [ ] **Open Telemetry and logging:** Implement observability features
- [ ] **Crawler:** Enhance web search with crawling
- [ ] **AI Agent Tools Registry:** An MCP tools hub to easily download and use community tools
- [ ] **Database for conversations:** Save users conversations in a database

## Guide to the roadmap

Every item on the roadmap is an issue, with a label that indicates each of the following:

- A **release phase** that describes the next expected phase of the roadmap item. See below for a guide to release phases.
- A **feature area** that indicates the area of the product to which the item belongs. For a list of current product areas, see below.
- A **feature** that indicates the feature or product to which the item belongs. For a list of current features, see below.
- One or more **product SKU** labels that indicate which product SKUs we expect the feature to be available in. For a list of current product SKUs, see below.
- One or more **deployment models** (cloud, server, and/or ae). Where not stated, features will generally come out Cloud first, and follow on Server and GHAE at or soon after GA.
- Once a feature is delivered, the **shipped** label will be applied to the roadmap issue and the issue will be closed with a comment linking to the relevant [Changelog](https://github.blog/changelog/) post.

## Roadmap stages

The roadmap is arranged on a project board to give a sense for how far out each item is on the horizon. Every product or feature is added to a particular project board column according to the quarter in which it is expected to ship next. Be sure to read the [disclaimer](#disclaimer) below since the roadmap is subject to change, especially further out on the timeline.  You'll also find an **Exploratory** column, which is used in conjunction with the **in design** and **exploring** release phase labels for when no timeframe is yet available.

GitHub Enterprise Server has major releases on a quarterly basis, and minor releases on a monthly basis. Once we know what version we are delivering a feature, we will update the issue to indicate that information.

## Disclaimer

Any statement in this repository that is not purely historical is considered a forward-looking statement. Forward-looking statements included in this repository are based on information available to GitHub as of the date they are made, and GitHub assumes no obligation to update any forward-looking statements. The forward-looking product roadmap does not represent a commitment, guarantee, obligation or promise to deliver any product or feature, or to deliver any product and feature by any particular date, and is intended to outline the general development plans. Customers should not rely on this roadmap to make any purchasing decision.
