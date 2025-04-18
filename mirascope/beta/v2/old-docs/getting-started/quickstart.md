---
icon: forward
---

# Quickstart

Get started using Mirascope in 30 seconds.

## Installation

{% tabs %}
{% tab title="uv" %}
```bash
# LLM Spec Interface
uv add mirascope

# All supported LLM providers
uv add "mirascope[models]"

# For (multiple) specific provider(s)
uv add "mirascope[openai,anthropic,google]"
```
{% endtab %}

{% tab title="pip" %}
```bash
# LLM Spec Interface
pip install mirascope

# All supported LLM providers
pip install "mirascope[models]"

# For (multiple) specific provider(s)
pip install "mirascope[openai,anthropic,google]"
```
{% endtab %}
{% endtabs %}

## Define a generation

> See [Generations](../generations.md) for more details.

A "generation" represents a model-agnostic LLM interaction:

```python
from mirascope import llm

@llm.generation(
    template="""
    [SYSTEM]
    
    
    [USER]
    Recommend a {{ genre }} book
    @if
    
    @end
    @for
    
    @end
    """
)
def recommend_book(genre: str) -> list[llm.Message]:
    return [
        llm.System("You are a librarian."),
        llm.User(f"Recommend a {genre} book"),
    ]
```

The `recommend_book` function defines a type-safe generation that takes a string `genre` as input and generates a standard `str` response.

### Run the generation

> See [Supported LLMs](../supported-llms.md) for a full list of providers and models that Mirascope supports.

At runtime, simply provide the model you want to power the generation as context:

```python
with llm.model("openai:gpt-4o"):
    response: llm.Response = recommend_book("fantasy")
    print(response.content)
    # > Certainly! I recommend "The Name of the Wind" by...
```

### Stream the generation

You can also stream the response:

<pre class="language-python"><code class="lang-python">with llm.model("anthropic:claude-3-7-sonnet-latest"):
<strong>    stream: llm.Stream = recommend_book.stream("fantasy")
</strong>    for chunk in stream:
        print(chunk.content, end="", flush=True)
        # > Certainly! I reco...
</code></pre>

### Async execution

You can easily run the generation asynchronously:

<pre class="language-python"><code class="lang-python"># inside an async code block
async with llm.model("mistral:mistral-large-latest"):
<strong>    response: llm.Response = await recommend_book.async("fantasy")
</strong>    print(response.content)
    # > Certainly! I recommend "The Name of the Wind" by...
</code></pre>

## Generations with Tools

> See [Tools](../tools.md) for more details.

Tools represent extended functionality that an LLM powering a Generation can request to use. We then call the tools on it's behalf and provide the results back in the next message. When the LLM is done calling tools, it generates its final output.

By default, Mirascope handles this interaction under the hood:

<pre class="language-python"><code class="lang-python">from mirascope import llm
    
<strong>@llm.tool()
</strong><strong>def available_books() -> dict[str,str]:
</strong><strong>    """Returns the books available for a given genre."""
</strong><strong>    return ["The Name of the Wind", "Mistborn: The Final Empire"]
</strong>
<strong>@llm.generation(tools=available_books)
</strong>def recommend_book(genre: str) -> list[llm.Message]:
    return [
        llm.User(f"Recommend a {genre} book"),
    ]
    
with llm.model("google:gemini-2.0-flash"):
    response: llm.Response = recommend_book("fantasy")
    print(response.content)
    # > Certainly. We have two fantasy books available: ...
</code></pre>

## Generations with Structured Outputs

> See [Structured Outputs](../structured-outputs.md) for more details.

By default, LLMs generate unstructured outputs. To structure their outputs, we define the response format of the generation:

<pre class="language-python"><code class="lang-python">from mirascope import llm

<strong>@llm.response_format()
</strong><strong>class Book:
</strong><strong>    title: str
</strong><strong>    author: str
</strong>    
<strong>@llm.generation(response_format=Book)
</strong>def recommend_book(genre: str) -> list[llm.Message]:
    return [
        llm.User(f"Recommend a {genre} book"),
    ]
    
with llm.model("xai:grok-3"):
    response: llm.Response[Book] = recommend_book("fantasy")
<strong>    print(response.format())
</strong>    # > title='The Name of the Wind' author='Patrick Rothfuss'
</code></pre>
