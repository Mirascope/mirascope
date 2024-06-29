# Supported LLM Providers

With new models dropping every week, it's important to be able to quickly test out different models. This can be an easy and powerful way to boost the performance of your application. Mirascope provides a unified interface that makes it fast and simple to swap between various providers.

We currently support the following providers:

- [OpenAI](https://platform.openai.com/docs/quickstart?context=python)
- [Anthropic](https://docs.anthropic.com/claude/docs/quickstart-guide)
- [Mistral](https://docs.mistral.ai/)
- [Cohere](https://docs.cohere.com/docs/the-cohere-platform)
- [Groq](https://console.groq.com/docs/quickstart)
- [Gemini](https://ai.google.dev/tutorials/get_started_web)

This also means that we support any providers that use these APIs.

!!! Note If there’s a provider you would like us to support that we don't yet support, please request the feature on our [GitHub Issues page](https://github.com/Mirascope/mirascope/issues) or [contribute](https://docs.mirascope.io/latest/CONTRIBUTING/) a PR yourself.

## Examples

Switching between providers with is as simple as can be:

1. Update your call decorator from `{old_provider}.call` to `{new_provider}.call`
2. Update any specific call params such as `model` or required keyword arguments for certain providers (like `max_tokens` for Anthropic).

=== "OpenAI”

```python
from mirascope.core import openai

@openai.call(model="gpt-4o")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

=== "Anthropic”

```python
from mirascope.core import anthropic

@anthropic.call(model="claude-3-5-sonnet-20240620", max_tokens=1000)
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

=== "Gemini”

```python
from mirascope.core import gemini

@gemini.call(model="gemini-1.0-pro-latest")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

=== "Mistral”

```python
from mirascope.core import mistral

@mistral.call(model="mistral-large-latest")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

=== "Cohere”

```python
from mirascope.core import cohere

@cohere.call(model="command-r-plus")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

=== "Groq”

```python
from mirascope.core import groq

@groq.call(model="mixtral-8x7b-32768")
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

## Custom Clients

If a provider has a custom endpoint you can call with their own API, it is accessible through Mirascope by setting `client` in the decorator. This is true for providers such as [Ollama](https://ollama.com/), [Anyscale](https://www.anyscale.com/), [Together](https://www.together.ai/), [AzureOpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service), and others that support the `OpenAI` API through a proxy.

```python
from mirascope.core import openai
from openai import AzureOpenAI, OpenAI

@openai.call("gpt-4o", client=AzureOpenAI(...))
def recommend_book(genre: str):
    """Recommend a {genre} book."""
    
@openai.call("llama3", client=OpenAI(base_url="BASE_URL", api_key="ollama"))
def recommend_book(genre: str):
    """Recommend a {genre} book."""
```

## `BasePrompt`

Mirascope’s `BasePrompt` class is intended for cases when you want to dynamically change model providers. Its `run()` function accepts all of our supported providers’ decorators, giving you flexibility to change providers in your code. Read more about `BasePrompt` here [link].
