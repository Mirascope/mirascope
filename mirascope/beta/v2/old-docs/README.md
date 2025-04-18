---
description: Welcome to the Mirascope OSS documentation! We're excited you're here.
icon: hand-wave
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Welcome

Mirascope is a powerful, flexible, and user-friendly library that implements [LLM Spec](https://app.gitbook.com/o/ezvv8NDXZ8o1gG96RwYr/s/ZkL2bVbbm5iaOPXwkqmS/) to simplify the process of working with LLMs through a standardized, model-agnostic interface.

```python
from mirascope import llm

# Define your generation.
@llm.generation()
def librarian(ctx: llm.Context, query: str) -> list[llm.Message]:
    return [
        llm.System("You are a librarian."),
        *ctx.history,
        llm.User(query),
    ]
    
# Power the generation with a specific model
with llm.model("google:gemini-2.0-flash-001"):
    response: llm.Response = librarian("What fantasy book should I read?")

print(response.content)
# > The capital of France is Paris.
```

<details>

<summary>Why Mirascope (we think you should read this)</summary>

_Because it's simple_. **And powerful**.

Mirascope meets you where you are in your journey building with LLMs.

It's modular, flexible, and purpose-built to work with your existing tools.

It's here to help you with the problems you're facing _today_.

And it's here to help you through the problems you may face tomorrow.

If you haven't already, we really recommend reading through [LLM Spec](https://app.gitbook.com/o/ezvv8NDXZ8o1gG96RwYr/s/ZkL2bVbbm5iaOPXwkqmS/) to get a deeper sense of what Mirascope is trying to accomplish.

If you're interested in [contributing](contributing.md) and hopping along for the ride, please do!

</details>

## Getting Started

<table data-view="cards"><thead><tr><th data-type="content-ref"></th></tr></thead><tbody><tr><td><a href="getting-started/quickstart.md">quickstart.md</a></td></tr><tr><td><a href="getting-started/observability-3.0.md">observability-3.0.md</a></td></tr><tr><td><a href="supported-llms.md">supported-llms.md</a></td></tr></tbody></table>



## Learn

<table data-card-size="large" data-view="cards"><thead><tr><th data-type="content-ref"></th></tr></thead><tbody><tr><td><a href="generations.md">generations.md</a></td></tr><tr><td><a href="tools.md">tools.md</a></td></tr><tr><td><a href="structured-outputs.md">structured-outputs.md</a></td></tr><tr><td><a href="graphs.md">graphs.md</a></td></tr></tbody></table>



## Advanced

<table data-card-size="large" data-view="cards"><thead><tr><th data-type="content-ref"></th></tr></thead><tbody><tr><td><a href="advanced/reliability.md">reliability.md</a></td></tr><tr><td><a href="advanced/evaluations.md">evaluations.md</a></td></tr><tr><td><a href="advanced/middleware.md">middleware.md</a></td></tr><tr><td><a href="advanced/model-context-protocol-mcp.md">model-context-protocol-mcp.md</a></td></tr></tbody></table>



## API Reference

...
