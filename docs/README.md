
<p align="center">
    <a href="https://www.mirascope.io"><img src="https://uploads-ssl.webflow.com/65a6fd6a1c3b2704d6217d3d/65b5674e9ceef563dc57eb11_Medium%20length%20hero%20headline%20goes%20here.svg" width="400" alt="Mirascope"/></a>
</p>

<p align="center">
    <em>Prompt Engineering focused on developer experience</em>
</p>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://docs.mirascope.io/" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

**Documentation**: <a href="https://docs.mirascope.io" target="_blank">https://docs.mirascope.io</a>

**Source Code**: <a href="https://github.com/Mirascope/mirascope" target="_blank">https://github.com/Mirascope/mirascope</a>

---

## Why use Mirascope?

**Mirascope** is a library purpose-built for prompt engineering on top of <a href="https://pydantic.dev" target="_blank">Pydantic</a>

**Mirascope** has a number of utility classes and functions such as `Prompt` and `messages` to enable more elegant prompt engineering (according to our opinionated point of view)

The primary goal of **Mirascope** is to improve **deverloper experience** through **autocomplete**, **inline errors**, and **validation** by providing better support for type checking and validation tools such as **mypy** and **Pydantic**. This in turn helps to ensure code is **maintainable** and **bug-free**. 

**Mirascope** also tries to improve **convenience** and **simplicity** when building LLM apps through lightweight convenience wrappers built around the OpenAI Python SDK. You can use the <a href="https://docs.together.ai/docs/openai-api-compatibility" target="_blank">Together AI API</a> to use these convenience wrappers with different models, such as <a href="https://mistral.ai/" target="_blank">Mistral AI</a>.

## 🚨 Warning

<!-- This library is going to blow your socks off, so make sure you're sitting down for what you're about to see... -->
Once you go mirascope, you never go backascope...

## Requirements

As **Mirascope** is built on top of **Pydantic**, which is the only strict requirement and will be included automatically during installation.

The Prompt CLI and LLM Convenience Wrappers have additional requirements, which you can opt-in to include if you're using those features.

## Installation

Install Mirascope and start building with LLMs in minutes.

```sh
$ pip install mirascope
```

This will install the `mirascope` package.

To include extra dependencies, run:

```sh
$ pip install mirascope[cli]     #  Prompt CLI
$ pip install mirascope[openai]  #  LLM Convenience Wrappers
$ pip install mirascope[all]     #  All Extras
```

## How to use

TBD

## Dive Deeper

-   Check out the [concepts section](concepts/pydantic_prompts.md) to dive deeper into the library and the core features that make it powerful.
-   You can take a look at [code examples](https://github.com/Mirascope/mirascope/tree/main/cookbook) in the repo that demonstrate how to use the library effectively.
-   The [API Reference](api/prompts.md) contains full details on all classes, methods, functions, etc.

## Contributing

Mirascope welcomes contributions from the community! See the [contribution guide](CONTRIBUTING.md) for more information on the development workflow. For bugs and feature requests, visit our [GitHub Issues](https://github.com/mirascope/mirascope/issues) and check out our [templates](https://github.com/Mirascope/mirascope/tree/main/.github/ISSUE_TEMPLATES).

## How To Help

Any and all help is greatly appreciated! Check out our page on [how you can help](HELP.md).

## Roadmap (What's on our mind)

- [ ] Better DX for Mirascope CLI (e.g. autocomplete)
- [ ] Evaluation and testing for prompts
- [ ] Prompt logging
- [X] Functions as OpenAI tools
- [ ] Agents
- [ ] RAG

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
