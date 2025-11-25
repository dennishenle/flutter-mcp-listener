---
marp: true
theme: default
paginate: true
backgroundColor: #222222
color: #ffffff
header: 'Controlling Flutter Applications with LLMs via MCP'
footer: 'Dennis Henle - Flutter Meetup'
---

# Controlling Flutter Applications with LLMs via MCP

---

# MCP - Model Context Protocol

## What is that and why the Hype?

### Understanding the Revolutionary Protocol That's Changing AI Integration
--- 

# What is MCP?
## Model Context Protocol Fundamentals

**MCP** is a standardized protocol developed by Anthropic (relesed Dezember 2024) for connecting AI models with external data sources, tools, and services in a secure, structured way.

---

# What is MCP? 

"MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems.
Using MCP, AI applications like Claude or ChatGPT can connect to data sources (e.g. local files, databases), tools (e.g. search engines, calculators) and workflows (e.g. specialized prompts)—enabling them to access key information and perform tasks.
Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect electronic devices, MCP provides a standardized way to connect AI applications to external systems." 

[modelcontextprotocol.io](https://modelcontextprotocol.io/docs/getting-started/intro)

---

# What is MCP?
### Core Concept:
- 🔌 **Universal Interface** - One protocol to connect any AI model to any data source
- 📡 **Real-time Context** - Dynamic information exchange during AI interactions  
- 🛡️ **Security-First Design** - Built-in authentication and sandboxing
- 🏗️ **Extensible Architecture** - Plugin-based ecosystem

Think of it as **"USB-C for AI"** - a universal connector that standardizes how AI systems interact with the world.

---

# MCP Architecture
## How It Works

Exactly like humans interact with applications to access data sources, AI models use MCP servers.

Just as humans can't directly connect to databases or APIs without proper interfaces, AI models need structured protocols to safely and efficiently access external resources. MCP provides this standardized bridge.

--- 

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │ Application UI  │    │  Data Sources   │
│                 │    │                 │    │                 │
│                 │◄──►│  • Protocol     │◄──►│  • Databases    │
│   Human         │    │  • Auth         │    │  • APIs         │
│                 │    │  • Routing      │    │  • Files        │
│                 │    │  • Caching      │    │  • Services     │
│                 │    │  • Security     │    │  • Tools        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Models     │    │   MCP Server    │    │  Data Sources   │
│                 │    │                 │    │                 │
│  • GPT-4        │◄──►│  • Protocol     │◄──►│  • Databases    │
│  • Claude       │    │  • Auth         │    │  • APIs         │
│  • Gemini       │    │  • Routing      │    │  • Files        │
│  • Local LLMs   │    │  • Caching      │    │  • Services     │
│                 │    │  • Security     │    │  • Tools        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

### Key Components:
- **MCP Client** - AI model interface
- **MCP Server** - Protocol handler and router  
- **Resources** - Data sources and tools
- **Tools** - Executable functions
- **Prompts** - Reusable prompt templates

---

# 🌟 The Positive Possibilities
## Why it's awesome

When we just take a look into [hub.docker.com](https://hub.docker.com/search?q=mcp) and search for "mcp" we already see what's possible. 

---

### It's what we waited for

The state of the art until MCP came out was

- **Fragmentation Crisis for ai tools**
    - Every tool had an own implementation how it's data got into the context
- **Context limitations**
    - No real-time data access during conversation
    - Model only knows it's training data
- **Seccurity nightmare**
    - Ad-hoc authentication methods
    - No standardized security practices

---

# I tried it out

With an MCP that can talk to my flutter app

---

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Model      │    │   MCP Server    │    │  Data Sources   │
│                 │    │                 │    │                 │
│                 │    │   Publishes a   │    │  • Databases    │
│   Cursor        │◄──►│   Webstream     │◄──►│  • APIs         │
│                 │    │   when called   │    │  • Files        │
│                 │    │   by Cursor     │    │  • Services     │
│                 │    │                 │    │  • Tools        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

--- 

## The MCP server

- Implemented with python
- standalone server, constantly running
- Provides MCP interface for the LLM

---

## Setup in cursor

```json
"WebstreamMCP": {
    "command": "docker",
    "args": [
        "exec",
        "-i",
        "webstream-mcp-server",
        "python",
        "/app/webstream_server.py"
    ]
}
```
---

## Startup MCP server

```bash
cd webstram-mcp-server
docker compose up
```

It should be available to watch in the browser now at
`localhost:8000`

---

## Call in MCP server

```

```

---

# Thank you 
