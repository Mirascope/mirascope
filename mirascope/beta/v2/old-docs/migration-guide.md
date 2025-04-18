---
icon: dove
---

# Migration Guide

As part of the `v1.23` release, certain interfaces have been deprecated in favor of new interfaces. We plan to fully remove these old interfaces in an upcoming release.

## Calls become Generations + Models

> See [Generations](generations.md) and [Models](models.md) for more details.

Previously, you would define a `call`-decorated function that would turn a [prompt template](prompts.md) into an LLM API call. It might have looked something like this:

```python
from mirascope import llm

@llm.call(provider="google", model="gemini-2.0-flash-001")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
    
response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
```

We've separated the `call` decorator twofold:

* `generation` decorator, which defines the generation in a model-agnostic way
* `model` context manager, which provides the LLM that powers the generation at runtime.

The `generation` decorator accepts existing prompt template functions:

<pre class="language-python"><code class="lang-python">from mirascope import llm

<strong>@llm.generation()
</strong>def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
    
<strong>with llm.model("google:gemini-2.0-flash-001", params=GenerationConfig):
</strong>    response: llm.Response = recommend_book("fantasy")
    print(response.content)
</code></pre>

The decorator turns `recommend_book` into a `Generation` that when called executes the generation using the model provided in the context.

The `Generation` class affords us a few additional benefits.

## Streaming becomes .stream

> See [Streaming](generations.md#streaming) for more details.

Rather than including `stream` as part of the definition, you can instead use the `.stream` method on the `Generation` class to execute the generation as a stream:

```python
with llm.model("google:gemini-2.0-flash-001"):
    stream: llm.StreamedResponse = recommend_book.stream("fantasy")
    for chunk in stream:
        print(chunk.content, end="", flush=True)
```

## Async becomes .async

> See [Async](generations.md#async) for more details.

We've done the same for asynchronous calls:

```python
async with llm.model("google:gemini-2.0-flash-001"):
    response: llm.Response = recommend_book.acall("fantasy")
    print(response.content)
    
    stream: llm.StreamedResponse = recommend_book.astream("fantasy")
    async for chunk in stream:
        print(chunk.content, end="", flush=True)
```

If your prompt template function is `async`, then only the `acall` and `astream` methods will be available.

## Tools become .tool functions

> See [Tools](tools.md) for more details.

The `generation` decorator only accepts tools defined as functions decorated with the `tool` decorator:

```python
from mirascope import llm

@llm.tool()
def available_books() -> list[str]:
    """Returns the list of available books."""
    return ["The Name of the Wind"]
    
@llm.generation(tools=[available_books])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"
    
response = recommend_book("fantasy")
print(response.content)
```

By default, tools will be called in a loop under the hood until the model generates its final response, but you can easily escape this default to regain full control.

## Response Model, JSON Mode, and Output Parser become Response Format

> See [Structured Outputs](structured-outputs.md) for more details

We've unified the interfaces for `response_model`, `json_mode`, and `output_parser` into a single interface that supports all three.

{% hint style="warning" %}
**The default (and only option) for response formatting is JSON mode.**

We've opted to completely separate tools from response formatting as a means of structuring outputs because of general confusion in the community.

You can still structure your outputs using tools, but you'll need to do so directly now. See the section on [using tools to structure outputs](structured-outputs.md#using-tools-to-structure-outputs) for more details.
{% endhint %}

```python
from mirascope import llm

@llm.response_format()
class Book:
    """A simple book."""
    title: str
    author: str
    
@llm.generation(response_format=Book)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."
    
with llm.model("google:gemini-2.0-flash-001"):
    response: llm.Response[Book] = recommend_book("fantasy")
    print(response.format())
```

By default, the `format` method of `ResponseFormat` instructs the model to output JSON of the given structure, which is then validated.

The `format` method can be overwritten, and it's docstring should instruct the model how to structure it's output such that the format method will work:

````python
from mirascope import llm

@llm.response_format()
class Book:
    """A simple book."""
    title: str
    author: str
    
    @classmethod
    def format(cls, response: llm.Response) -> "Book":
        """Returns the response formatted as a book.
        
        @formatting_instructions
        ```plaintext
        {title} by {author}
        ```
        @end
        """
        title, author = response.content.split(" by ")
        return cls(title, author)
````

You can also define your response format using Pydantic, which will use `model_json_schema` and `model_validate` as the format method:

```python
from mirascope import llm
from pydantic import BaseModel

@llm.response_format()
class Book(BaseModel):
    """A simple book."""
    title: str
    author: str
```

## No more integrations

> See [Reliability](advanced/reliability.md) and [Middleware](advanced/middleware.md) for more details.

We believe that Mirascope is flexible enough to easily integrate anywhere in your stack with any tool as implemented — it's just Python functions.

We have also implemented opt-in OpenTelemetry compatible instrumentation using [Lilypad](https://app.gitbook.com/o/ezvv8NDXZ8o1gG96RwYr/s/pGMXFubFyptiiuRdVj0d/), which integrates nicely with any tooling that supports OpenTelemetry (and extra nicely if it supports [LLM Spec](https://app.gitbook.com/o/ezvv8NDXZ8o1gG96RwYr/s/ZkL2bVbbm5iaOPXwkqmS/)).

For cases where the tools you're using don't provide great reusable interfaces, you can use this type-safe decorator code as a template for implementing reusable decorators:

```python
```
