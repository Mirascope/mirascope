# Logfire

[Logfire](https://docs.pydantic.dev/logfire/), a new tool from Pydantic, is built on OpenTelemetry. Since Pydantic powers many of Mirascope's features, it's appropriate for us to ensure seamless integration with them.

You can install the necessary packages directly or using the `logfire` extras flag:

```python
pip install "mirascope[logfire]"
```

## How to use Logfire with Mirascope

### Calls

The `with_logfire` decorator can be used on all Mirascope functions to automatically log calls across all of our [supported LLM providers](../learn/calls.md#supported-providers).

```python
import logfire
from mirascope.core import anthropic, prompt_template
from mirascope.integrations.logfire import with_logfire

logfire.configure()


def format_book(title: str, author: str):
    return f"{title} by {author}"


@with_logfire()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


print(recommend_book("fantasy"))
# > Certainly! I'd be happy to recommend a fantasy book for you. To provide...
```

This will give you:

* A span called `recommend_book` that captures items like the prompt template, templating properties and fields, and input/output attributes
* Human-readable display of the conversation with the agent
* Details of the response, including the number of tokens used

![logfire-call](../assets/logfire-call.png)

### Streams

You can capture streams exactly the same way:

```python
import logfire
from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire

logfire.configure()


@with_logfire()
@openai.call(
    model="gpt-4o-mini",
    stream=True,
    call_params={"stream_options": {"include_usage": True}},
)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
# > I recommend "The Name of the Wind" by Patrick Rothfuss. It’s the first book...
```

For some providers, certain `call_params` will need to be set in order for usage to be tracked.

!!! note "Logged Only On Exhasution"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

### Response Models

Since Mirascope `response_model` is built on top of [Pydantic](https://docs.pydantic.dev/latest/), you can use the [Pydantic Plugin](https://docs.pydantic.dev/latest/concepts/plugins/) to track additional logs and metrics about model validation, which you can enable using the `pydantic_plugin` configuration.

This can be particularly useful when [extracting structured information using LLMs](../learn/response_models.md):

```python
import logfire
from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))


class Book(BaseModel):
    title: str
    author: str


@with_logfire()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...

print(recommend_book("fantasy"))
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

This will give you:

* Tracking for validation of Pydantic models
* All the information from call with a `response_model` output.

![logfire-response-model](../assets/logfire-response-model.png)

You can also set `stream=True` with the same rules as streaming a call. Note that the Pydantic Plugin will log many times if you are streaming a `response_model`, so it is recommended to wrap the Mirascope call in a function.

## FastAPI

You can take advantage of existing instruments from Logfire and easily integrate with FastAPI and Mirascope.

```python
import logfire
from fastapi import FastAPI
from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire
from pydantic import BaseModel

app = FastAPI()
logfire.configure()
logfire.instrument_fastapi(app)


class Book(BaseModel):
    title: str
    author: str


@app.post("/")
@with_logfire()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...
```

## Instrumenting LLM Providers directly

If you choose not to use our `with_logfire` decorator, you can manually instrument the client using Logfire instruments.

Here is an example Mirascope call using `logfire.instrument_openai`:

```python
import logfire
from mirascope.core import openai, prompt_template
from openai import Client

client = Client()
logfire.configure()
logfire.instrument_openai(client)


@openai.call(model="gpt-4o-mini", client=client)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


recommend_book("fantasy")
```
