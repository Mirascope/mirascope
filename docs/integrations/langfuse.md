# Langfuse

Mirascope provides out-of-the-box integration with [Langfuse](https://langfuse.com/).

## How to use Langfuse with Mirascope

```python
pip install langfuse

from mirascope.integrations.langfuse import with_langfuse
```

`with_langfuse` is a decorator that can be used on all Mirascope functions to automatically log all our [supported LLM providers](ADD LINK).

## Examples

### Call

A Mirascope call with tools:

```python
from mirascope.core import anthropic, prompt_template
from mirascope.integrations.langfuse import with_langfuse

def format_book(title: str, author: str):
    return f"{title} by {author}"

@with_langfuse
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...

print(recommend_book("fantasy"))
# > Certainly! I'd be happy to recommend a fantasy book for you. However, to provide a specific recommendation, 
#   I'll need to use the available tool to format the book information correctly. Let me suggest a popular and well-regarded fantasy novel.
```

This will give you:

* A trace around the `recommend_book` function that captures items like the prompt template, and input/output attributes and more.
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

![langfuse-call-tool](../assets/langfuse-call-tool.png)

### Stream

Streaming a Mirascope call:

```python
from mirascope.core import openai, prompt_template
from mirascope.integrations.langfuse import with_langfuse

@with_langfuse
@openai.call(
    model="gpt-4o-mini",
    stream=True,
    call_params={"stream_options": {"include_usage": True}},
)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
# > I recommend **"The Name of the Wind"** by Patrick Rothfuss. It's the first book in the "Kingkiller Chronicle" series and follows the story of Kvothe, a gifted young
#   man with a mysterious past, as he recounts his adventures and the journey that led him to become a legendary figure. The writing is beautifully lyrical, and Rothfuss 
#   builds a rich, immersive world with intricate magic systems and memorable characters. If you enjoy deep storytelling and character-driven plots, this book is a great 
#   choice!
```

For some providers, certain `call_params` will need to be set in order for usage to be tracked.
Also note that the span will not be logged until the stream has been exhausted.

### Response Model

A Mirascope call extracting structured information:

```python
from pydantic import BaseModel

from mirascope.core import openai, prompt_template
from mirascope.integrations.langfuse import with_langfuse


class Book(BaseModel):
    title: str
    author: str


@with_langfuse
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

This will give you all the information from call with a `response_model` output. You can also set `stream=True` with the same rules as streaming a call.

![langfuse-response-model](../assets/langfuse-response-model.png)

## Using Langfuse directly with Mirascope

If you choose not to use our `with_langfuse` decorator, you can use Langfuse's wrapper of the OpenAI client.

Here is an example Mirascope call using `langfuse.openai`:

```python
from langfuse.openai import OpenAI

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", client=OpenAI())
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# > I recommend **"The Name of the Wind"** by Patrick Rothfuss. It's the first book in the *Kingkiller Chronicle* series and follows the story of Kvothe, a gifted young 
#   man with a mysterious past. The narrative weaves elements of magic, music, and adventure, with rich world-building and memorable characters. It's both a coming-of-age 
#   tale and an epic fantasy that has garnered a loyal following for its lyrical prose and deep emotional resonance. Enjoy your reading!
```
