# Getting started with Mirascope

This library intends to give developers a better way to build with LLMs that integrates seamlessly into your workflow, starting with better prompt management and core LLM interaction calls. We’re building the de facto pythonic prompt templating and LLM-interaction library.

---

[![GitHub stars](https://img.shields.io/github/stars/Mirascope/mirascope.svg)](https://github.com/Mirascope/mirascope/stargazers)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen)](https://docs.mirascope.io/)
[![](https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Mirascope/mirascope/actions/workflows/tests.yml)
[![GitHub issues](https://img.shields.io/github/issues/Mirascope/mirascope.svg)](https://github.com/Mirascope/mirascope/issues)
[![Github discussions](https://img.shields.io/github/discussions/Mirascope/mirascope)](https:github.com/Mirascope/mirascope/discussions)
[![GitHub license](https://img.shields.io/github/license/Mirascope/mirascope.svg)](https://github.com/Mirascope/mirascope/blob/main/LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/mirascope.svg)](https://pypi.python.org/pypi/mirascope)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/mirascope.svg)](https://pypi.python.org/pypi/mirascope)

---

## Why use Mirascope?

- **Easy**: Designed for ease of use, Mirascope features an intuitive interface and a minimal learning curve
- **Intuitive**: Get editor support for prompts, eliminating the need to dig through documentation
- **Durable**: Mirascope offers versatile and adaptable functionality, allowing seamless integration with custom solutions
- **Integration**: Leveraging Pydantic, Mirascope offers easy integration with JSON Schema and other tools
- **Maintainability**: Reduce prompt-related bugs and organize prompts with provided utilities

## Installation

Install Mirascope and start building with LLMs in minutes.

```sh
$ pip install mirascope
```

This will install the `mirascope` package and CLI.

## A Simple Mirascope Example

```python
from mirascope import OpenAIChat, Prompt

class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

prompt = BookRecommendationPrompt(topic="coding")
print(str(prompt))

model = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
res = model.create(prompt)
print(str(res))
```

```
Can you recommend some books on coding?

Certainly! Here are some highly recommended books on coding: ...
```

## Dive Deeper

-   Check out the concepts section to dive deeper into the library and the core features that make it powerful, such as [pydantic prompts](concepts/pydantic_prompts.md) and the [Mirascope CLI](concepts/mirascope_cli.md).
-   You can follow along with more detailed [examples](cookbook/simple_call.md) to get a better understanding of how to utilize the library to effectively model your data. You can also take a look at [code examples](https://github.com/Mirascope/mirascope/tree/main/cookbook) in the repo.
-   The [API Reference](api/prompts.md) contains full details on all classes, methods, functions, etc.

## Contributing

Mirascope welcomes contributions from the community! See the [contribution guide](CONTRIBUTING.md) for more information on the development workflow. For bugs and feature requests, visit our [GitHub Issues](https://github.com/mirascope/mirascope/issues) and check out our [templates](https://github.com/Mirascope/mirascope/tree/main/.github/ISSUE_TEMPLATES).

## How To Help

Any and all help is greatly appreciated! Check out our page on [how you can help](HELP.md).

## Roadmap (What's on our mind)

- [ ] Agents
- [ ] RAG
- [ ] Functions as OpenAI tools
- [ ] Testing for prompts
- [ ] Add more LLMs
- [ ] Prompt Response tracking
- [ ] Database support for versioning
- [ ] Better DX for Mirascope CLI (e.g. autocomplete)

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
