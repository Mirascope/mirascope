
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

**Mirascope** is a library purpose-built for Prompt Engineering on top of <a href="https://pydantic.dev" target="_blank">Pydantic</a>:

* **Intuitive**: Editor support that you expect (e.g. **autocompletion**, **inline errors**)
* **Peace of Mind**: Pydantic together with our Prompt CLI **eliminate prompt-related bugs**.
* **Durable**: Seamlessly customize and extend functionality. **Never maintain a fork**.
* **Integration**: Easily integrate with **JSON Schema** and other tools such as **FastAPI**
* **Convenience**: Tooling that is **clean**, **elegant**, and **delightful** that **you don't need to maintain**.
* **Open**: Dedication to building **open-source tools** you can use with **your choice of LLM**.

## 🚨 Warning: Strong Opinion

Prompt Engineering is just engineering. Beyond simple toy examples (that aren't useful), prompting quickly becomes complex. Separating prompts from the engineering workflow will only put limitations on what you can build with LLMs. We firmly believe that prompts are far more than "just f-strings" and thus require developer tools that are purpose-built to make building these more complex prompts as easy as possible.

Furthermore, the best developer experience requires the following, which we strive to uphold:

* *Simplicity through idiomatic syntax* -> ***Faster and more reliable releases***
* *Semi-opinionated methods* -> ***Reduced complexity that speeds up development***
* *Reliability through validation* -> ***More robust applications with fewer bugs***
* *High-quality up-to-date documentation* -> ***Trust and reliability***

Speeds up development
Results in fewer bugs and iterations
Helps to guarantee robust applications
Enables faster and more reliable releases
Reduces complexity and risk through maximal composability and customizability

Once you go mirascope, you'll never go back...ascope

## Requirements

**Pydantic** is the only strict requirement, which will be included automatically during installation.

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

WIP

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
