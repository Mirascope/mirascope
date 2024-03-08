# Why we’re building Mirascope

When OpenAI first announced GPT-3.5 turbo model, we were excited to use it in our own backend API server. However, what we quickly realized was that we spent the majority of time building developer tooling around the OpenAI SDK rather than actually prompt engineering. When asking other developers how they are using the OpenAI SDK, we found that the answers were rather similar to our own situation. So we set out to build an Open Source Library such that others can prompt engineer with speed, robustness, and simplicity.

## Pydantic Prompts

Our internal tooling for working with GPT leveraged Pydantic which became the foundation for Mirascope.

The [`BasePrompt`](../api/base/prompt.md#mirascope.base.prompt.Prompt) class is the core of Mirascope, which extends Pydantic's [`BaseModel`](https://docs.pydantic.dev/latest/api/base_model/). The class leverages the power of python to make writing more complex prompts as easy and readable as possible. The docstring is automatically formatted as a prompt so that you can write prompts in the style of your codebase.

## Why use Mirascope?

### You get all of the [benefits of using Pydantic](https://docs.pydantic.dev/latest/#why-use-pydantic)

- type hints, json schema, customization, ecosystem, production-grade

### Speeds up development

- Fewer bugs through validation
- Auto-complete, editor (and linter) support for errors

### Easy to learn

- You only need to learn Pydantic

### Standardization and compatibility

- Integrations with other libraries that use JSON Schema such as OpenAPI and FastAPI means writing less code.

### Customization

- Everything is Pydantic or basic python, so changing anything is as easy as overriding what you want to change

**All of the above helps lead to production ready code**
