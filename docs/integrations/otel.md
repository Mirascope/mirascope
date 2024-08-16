# OpenTelemetry

Mirascope provides out-of-the-box integration with [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/).

You can install the necessary packages directly or using the `opentelemetry` extras flag:

```python
pip install "mirascope[opentelemetry]"
```

## How to use OpenTelemetry with Mirascope

### Calls

The `with_otel` decorator can be used on all Mirascope functions to automatically log calls across all [supported LLM providers](../learn/calls.md#supported-providers).

Here is a simple example using tools:

```python
from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import with_otel, configure

configure()


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@with_otel()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


print(recommend_book("fantasy"))
# > Certainly! I'd be happy to recommend a fantasy book for you. To provide...
```

This will give you:

* A span called `recommend_book` that captures items like the prompt template, templating properties and fields, and input/output attributes
* Details of the response, including the number of tokens used

```python
{
    "name": "recommend_book",
    "context": {
        "trace_id": "0xb29c6012043ccf89f7883ac90070ef07",
        "span_id": "0xcb73bc686151b357",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-08-08T00:24:51.405611Z",
    "end_time": "2024-08-08T00:24:51.408011Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "gen_ai.system": "Recommend a {genre} book.",
        "gen_ai.request.model": "claude-3-5-sonnet-20240620",
        "gen_ai.request.max_tokens": 0,
        "gen_ai.request.temperature": 0,
        "gen_ai.request.top_p": 0,
        "gen_ai.response.model": "claude-3-5-sonnet-20240620",
        "gen_ai.response.id": "msg_01K8Zrk2VY6B2JC6G8GuRmjv",
        "gen_ai.response.finish_reasons": [
            "tool_use"
        ],
        "gen_ai.usage.completion_tokens": 149,
        "gen_ai.usage.prompt_tokens": 393,
        "async": false
    },
    "events": [
        {
            "name": "gen_ai.content.prompt",
            "timestamp": "2024-08-08T00:24:51.407996Z",
            "attributes": {
                "gen_ai.prompt": "{\"content\": \"Recommend a fantasy book.\", \"role\": \"user\"}"
            }
        },
        {
            "name": "gen_ai.content.completion",
            "timestamp": "2024-08-08T00:24:51.408004Z",
            "attributes": {
                "gen_ai.completion": "{\"content\": [{\"text\": \"Certainly! I'd be happy to recommend a fantasy book for you. To provide a proper recommendation using the available tool, I'll need to use the \\\"format_book\\\" function. However, since you haven't specified a particular book, I'll choose a popular fantasy novel to recommend. Let me use the tool to format the recommendation for you.\", \"type\": \"text\"}, {\"id\": \"toolu_01DDcMmjDzMLTupLFvYuGg9m\", \"input\": {\"title\": \"The Name of the Wind\", \"author\": \"Patrick Rothfuss\"}, \"name\": \"format_book\", \"type\": \"tool_use\"}], \"role\": \"assistant\"}"
            }
        }
    ],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.22.0",
            "service.name": "unknown_service"
        },
        "schema_url": ""
    }
}
```

### Streams

You can capture streams exactly the same way:

```python
from mirascope.core import openai, prompt_template
from mirascope.integrations.otel import with_otel, configure

configure()

@with_otel()
@openai.call(
    model="gpt-4o-mini",
    stream=True,
    call_params={"stream_options": {"include_usage": True}},
)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
# > I recommend "The Name of the Wind" by Patrick Rothfuss. It’s the first book in the "Kingkiller Chronicle" series...
```

For some providers, certain `call_params` will need to be set in order for usage to be tracked.

!!! note "Logged Only On Exhasution"

    When logging streams, the span will not be logged until the stream has been exhausted. This is a function of how streaming works.

### Response Models

Setting `response_model` also behaves the exact same way:

```python
from mirascope.core import openai, prompt_template
from mirascope.integrations.otel import with_otel, configure
from pydantic import BaseModel

configure()


class Book(BaseModel):
    title: str
    author: str


@with_otel()
@openai.call(model="gpt-4o-mini", response_model=Book)
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str):
    ...


print(recommend_book("fantasy"))
# > title='The Name of the Wind' author='Patrick Rothfuss'
```

This will give you all the information from call with a `response_model` output inside `gen_ai.completion`.

```python
{
    "name": "recommend_book",
    "context": {
        "trace_id": "0xd0806c4943f9e6ca3c4a2bde7ace6d84",
        "span_id": "0xb5130f9f98a44df8",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-08-08T00:28:46.378062Z",
    "end_time": "2024-08-08T00:28:46.378480Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "gen_ai.system": "Recommend a {genre} book.",
        "gen_ai.request.model": "gpt-4o-mini",
        "gen_ai.request.max_tokens": 0,
        "gen_ai.request.temperature": 0,
        "gen_ai.request.top_p": 0,
        "gen_ai.response.model": "gpt-4o-mini-2024-07-18",
        "gen_ai.response.id": "chatcmpl-9tlJFYXkJoC8HeONA5rCBPbwnDzP3",
        "gen_ai.response.finish_reasons": [
            "tool_calls"
        ],
        "gen_ai.usage.completion_tokens": 24,
        "gen_ai.usage.prompt_tokens": 71,
        "async": false
    },
    "events": [
        {
            "name": "gen_ai.content.prompt",
            "timestamp": "2024-08-08T00:28:46.378461Z",
            "attributes": {
                "gen_ai.prompt": "{\"content\": \"Recommend a fantasy book.\", \"role\": \"user\"}"
            }
        },
        {
            "name": "gen_ai.content.completion",
            "timestamp": "2024-08-08T00:28:46.378473Z",
            "attributes": {
                "gen_ai.completion": "{\"title\":\"The Name of the Wind\",\"author\":\"Patrick Rothfuss\"}"
            }
        }
    ],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.22.0",
            "service.name": "unknown_service"
        },
        "schema_url": ""
    }
}
```

You can also set `stream=True` when using `response_model`, which has the same behavior as standard streaming.

## Sending to an observability tool

Now, we want to send our spans to an actual observability tool so that we can monitor our traces. There are many observability tools out there, but the majority of them can collect OpenTelemetry data. You can pass in processors as an argument of configure() so that you can send the spans to the observability tool you choose:

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from mirascope.integrations.otel import configure

OBSERVABILITY_TOOL_ENDPOINT = "..."
configure(
    processors=[
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=f"https://{OBSERVABILITY_TOOL_ENDPOINT}/v1/traces",
            )
        )
    ]
)
```

You should refer to your observability tool's documentation to find the endpoint. If there is an observability backend that you would like for us to integrate out-of-the-box, create a [GitHub Issue](https://github.com/Mirascope/mirascope/issues) or let us know in our [Slack](https://join.slack.com/t/mirascope-community/shared_invite/zt-2ilqhvmki-FB6LWluInUCkkjYD3oSjNA) community.

