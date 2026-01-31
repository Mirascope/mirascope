---
title: "Registry"
description: "Browse and install reusable AI tools, agents, and prompts from the Mirascope Registry"
url: "https://mirascope.com/registry"
---

# Mirascope Registry

Version: 2.1.0

Browse and install reusable AI components for your Mirascope projects.

## Available Items

### Tools

- **calculator**: Basic arithmetic operation tools (add, subtract, multiply, divide) for LLM agents.
  Install: `mirascope registry add calculator`

## Installation

**Python:**
```bash
mirascope registry add <item-name>
```

**TypeScript:**
```bash
npx mirascope registry add <item-name>
```

## Initialize Configuration

Create a `mirascope.json` configuration file in your project:

```bash
mirascope registry init
```

This creates a configuration file with default paths for different item types.

## Programmatic Access

- Registry index: https://mirascope.com/registry/r/index.json
- Python item: https://mirascope.com/registry/r/{name}.python.json
- TypeScript item: https://mirascope.com/registry/r/{name}.typescript.json

## Questions?

Join our community at https://mirascope.com/discord-invite to ask the team directly.
