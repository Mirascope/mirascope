<div align="center" justiry="start">
    <a href="https://mirascope.com">
        <img align="bottom" src="https://github.com/Mirascope/mirascope/assets/99370834/e403d7ee-f8bc-4df1-b2d0-33763f021c89" alt="Frog Logo" width="84"/><br><img align="bottom" src="https://uploads-ssl.webflow.com/65a6fd6a1c3b2704d6217d3d/65b5674e9ceef563dc57eb11_Medium%20length%20hero%20headline%20goes%20here.svg" width="400" alt="Mirascope"/>
    </a>
</div>

<p align="center">
    <a href="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml" target="_blank"><img src="https://github.com/Mirascope/mirascope/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests"/></a>
    <a href="https://codecov.io/github/Mirascope/mirascope" target="_blank"><img src="https://codecov.io/github/Mirascope/mirascope/graph/badge.svg?token=HAEAWT3KC9" alt="Coverage"/></a>
    <a href="https://mirascope.com/WELCOME" target="_blank"><img src="https://img.shields.io/badge/docs-available-brightgreen" alt="Docs"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/v/mirascope.svg" alt="PyPI Version"/></a>
    <a href="https://pypi.python.org/pypi/mirascope" target="_blank"><img src="https://img.shields.io/pypi/pyversions/mirascope.svg" alt="Stars"/></a>
    <a href="https://github.com/Mirascope/mirascope/blog/dev/LICENSE"><img src="https://img.shields.io/github/license/Mirascope/mirascope.svg" alt="License"/></a>
    <a href="https://github.com/Mirascope/mirascope/stargazers" target="_blank"><img src="https://img.shields.io/github/stars/Mirascope/mirascope.svg" alt="Stars"/></a>
</p>

---

Mirascope is a powerful, flexible, and user-friendly library that simplifies the process of working with LLMs through a unified interface that works across various supported providers, including [OpenAI](https://openai.com/), [Anthropic](https://www.anthropic.com/), [Mistral](https://mistral.ai/), [Google (Gemini/Vertex)](https://googleapis.github.io/python-genai/), [Groq](https://groq.com/), [Cohere](https://cohere.com/), [LiteLLM](https://www.litellm.ai/), [Azure AI](https://azure.microsoft.com/en-us/solutions/ai), and [Bedrock](https://aws.amazon.com/bedrock/).

Whether you're generating text, extracting structured information, or developing complex AI-driven agent systems, Mirascope provides the tools you need to streamline your development process and create powerful, robust applications.

## 30 Second Quickstart

Install Mirascope, specifying the provider(s) you intend to use, and set your API key:

```bash
pip install "mirascope[openai]"
export OPENAI_API_KEY=XXXXX
```

Make your first call to an LLM to extract the title and author of a book from unstructured text:

```python
from mirascope import llm
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book)
def extract_book(text: str) -> str:
    return f"Extract {text}"

book = extract_book("The Name of the Wind by Patrick Rothfuss")
assert isinstance(book, Book)
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
```

## Tutorials

Check out our [quickstart tutorial](https://mirascope.com/tutorials/getting_started/quickstart) and many other tutorials for an interactive way to getting started with Mirascope.

## Usage

For a complete guide on how to use all of the various features Mirascope has to offer, read through our [Learn](https://mirascope.com/learn) documentation.

## Versioning

Mirascope uses [Semantic Versioning](https://semver.org/).

## Licence

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/mirascope/blob/dev/LICENSE).
