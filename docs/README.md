# Mirascope

<div align="center">
    <table>
        <tr>
            <td align="center" width="420"><em>Simplicity through idiomatic syntax</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>Faster and more reliable releases</em></strong></td>
        </tr>
        <tr>
            <td align="center" width="420"><em>Semi-opinionated methods</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>Reduced complexity that speeds up development</em></strong></td>
        </tr>
        <tr>
            <td align="center" width="420"><em>Reliability through validation</em></td>
            <td align="center">→</td>
            <td align="center" width="420"><strong><em>More robust applications with fewer bugs</em></strong></td>
        </tr>
    </table>
</div>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://docs.mirascope.io/" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

**Mirascope** is an open-source Python toolkit built on top of [Pydantic](https://docs.pydantic.dev/latest/) that makes working with Large Language Models (LLMs):

- **Durable**: Seamlessly **customize and extend functionality**.
- **Intuitive**: Editor support that you expect (e.g. **autocompletion**, **inline errors**)
- **Clean**: Pydantic together with our Prompt CLI **eliminates prompt-related bugs**.
- **Integrable**: Easily integrate with **JSON Schema** and other tools such as [FastAPI](https://fastapi.tiangolo.com/)
- **Convenient**: Tooling that is **clean**, **elegant**, and **delightful** that **you don't need to maintain**.
- **Open**: Dedication to building **open-source tools** you can use with **your choice of LLM**.

We support any model that works with the OpenAI API, as well as other models such as Gemini.

## Installation

Install Mirascope and start building with LLMs in minutes.

```bash
pip install mirascope
```

You can also install additional optional dependencies if you’re using those features:

```bash
pip install mirascope[wandb]   # WandbPrompt
pip install mirascope[gemini]  # GeminiPrompt, ...
```

## Usage

With Mirascope, everything happens with prompts. The idea is to colocate any functionality that may impact the quality of your prompt — from the template variables to the temperature — so that you don’t need to worry about code changes external to your prompt affecting quality. For simple use-cases, we find that writing prompts as docstrings provides enhanced readability:

```python
from mirascope.openai import OpenAICallParams, OpenAIPrompt


class BookRecommendation(OpenAIPrompt):
    """Please recommend a {genre} book."""

    genre: str

    call_params = OpenAICallParams(
        model="gpt-4",
        temperature=0.3,
    )


recommendation = BookRecommendation(genre="fantasy").create()
print(recommendation)
#> I recommend "The Name of the Wind" by Patrick Rothfuss. It is...
```

If you add any of the OpenAI message roles (SYSTEM, USER, ASSISTANT, TOOL) as keywords to your prompt docstring, they will automatically get parsed into a list of messages:

```python
from mirascope.openai import OpenAIPrompt


class BookRecommendation(OpenAIPrompt):
    """
    SYSTEM:
    You are the world's greatest librarian.

    USER:
    Please recommend a {genre} book.
    """

    genre: str


prompt = BookRecommendation(genre="fantasy")
print(prompt.messages)
#> [{'role': 'system', 'content': "You are the world's greatest librarian."},
#   {'role': 'user', 'content': 'Please recommend a fantasy book.'}]
```

If you want to write the messages yourself instead of using the docstring message parsing, there’s nothing stopping you!

```python
from mirascope.openai import OpenAIPrompt
from openai.types.chat import ChatCompletionMessageParam


class BookRecommendation(OpenAIPrompt):
    """This is now just a normal docstring.

    Note that you'll lose any functionality dependent on it,
    such as `template`.
    """

    genre: str

    @property
    def messages(self) -> list[ChatCompletionMessageParam]:
        """Returns the list of OpenAI prompt messages."""
        return [
            {"role": "system", "content": "You are the world's greatest librarian."},
            {"role": "user", "content": f"Please recommend a {self.genre} book."},
        ]


recommendation = BookRecommendation(genre="fantasy").create()
print(recommendation)
#> I recommend "The Name of the Wind" by Patrick Rothfuss. It is...
```

### Create, Stream, Extract

Prompt classes such as `OpenAIPrompt` have three methods for interacting with the LLM:

- [`create`](concepts/generating_content.md): Generate a response given a prompt. This will generate raw text unless tools are provided as part of the `call_params`.
- [`stream`](concepts/streaming_generated_content.md): Same as `create` except the generated response is returned as a stream of chunks. All chunks together become the full completion.
- [`extract`](concepts/extracting_structured_information_using_llms.md): Convenience tooling built on top of tools to make it easy to extract structured information given a prompt and schema.

### Using Different LLM Providers

The `OpenAIPrompt` class supports any endpoint that supports the OpenAI API, including (but not limited to) [Anyscale](https://www.anyscale.com/endpoints), [Together](https://api.together.xyz/playground/chat/meta-llama/Llama-2-70b-chat-hf), and [Groq](https://groq.com/). Simply update the `base_url` and set the proper api key in your environment:

```python
import os

from mirascope.openai import OpenAICallParams, OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "TOGETHER_API_KEY"


class BookRecommendation(OpenAIPrompt):
    """Please recommend a {genre} book."""

    genre: str

    call_params = OpenAICallParams(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            base_url="https://api.together.xyz/v1",
    )


recommendation = BookRecommendation(genre="fantasy").create()
```

We also support [other providers](concepts/using_different_model_providers.md) such as Gemini.

## Dive Deeper

- Learn why colocation is so important and how combining it with the [Mirascope CLI](concepts/using_the_mirascope_cli.md) makes engineering better prompts easy.
- Check out how to [write better prompts](concepts/writing_prompts.md) using Mirascope.
- Become a master of [extracting structured information using LLMs](concepts/extracting_structured_information_using_llms.md).
- Take a look at how Mirascope makes using [tools (function calling)](concepts/tools_(function_calling).md) simple and clean.
- The [API Reference](api/index.md) contains full details on all classes, methods, functions, etc.

## Examples

You can find more usage examples in our [examples](https://github.com/Mirascope/mirascope/tree/main/examples) directory, such as how to easily integrate with FastAPI.

We also have more detailed walkthroughs in our Cookbook docs section. Each cookbook has corresponding full code examples in the [cookbook](cookbook/wandb_chain.md) directory.

## What’s Next?

We have a lot on our minds for what to build next, but here are a few things (in no particular order) that come to mind first:

- [x]  Extracting structured information using LLMs
- [ ]  Agents
- [ ]  Support for more LLM providers:
    - [ ]  Anthropic
    - [ ]  Mistral
    - [ ]  HuggingFace
- [ ]  Integrations:
    - [x]  Weights & Biases
    - [x]  LangSmith
    - [ ]  … tell us what you’d like integrated!
- [ ]  Evaluating prompts and their quality by version
- [ ]  Additional docstring parsing for more complex messages

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/main/LICENSE).
