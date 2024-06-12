# OpenTelemetry

Mirascope provides out-of-the-box integration with [OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/).

## Setting up Manual Instrumentation

Due to the detailed about of data Mirascope needs to collect about calls, we use manual instrumentation. Thankfully, it is low-code on the user-end so Mirascope still offers convenience.

First thing to do is install mirascope opentelemetry:

```bash
pip install mirascope[opentelemetry]
```

This code will look pretty familiar with users who already use OpenTelemetry. Here's a refresher:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)
```

## With Mirascope

Calling the `configure()` function will call the code above. This is a one time setup that should be done when your app loads for the first time. Afterwards, you can add the `@with_otel` decorator to any of your Mirascope classes to get instrumentation.

```python
import os
from typing import Literal

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from pydantic import BaseModel
from mirascope.openai.extractors import OpenAIExtractor
from mirascope.openai.types import OpenAICallParams
from mirascope.otel import with_otel, configure

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

os.environ["OTEL_SERVICE_NAME"] = "YOUR_SERVICE_NAME"


configure()
# -- OR --
# provider = TracerProvider()
# processor = BatchSpanProcessor(ConsoleSpanExporter())
# provider.add_span_processor(processor)

# # Sets the global default tracer provider
# trace.set_tracer_provider(provider)

class TaskDetails(BaseModel):
    description: str
    due_date: str
    priority: Literal["low", "normal", "high"]


@with_otel
class TaskExtractor(OpenAIExtractor[TaskDetails]):
    extract_schema: type[TaskDetails] = TaskDetails
    prompt_template = """
    Extract the task details from the following task:
    {task}
    """

    task: str

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo",
    )


task = "Submit quarterly report by next Friday. Task is high priority."
task_details = TaskExtractor(
    task=task
).extract()  # this will be logged automatically to console
assert isinstance(task_details, TaskDetails)
print(task_details)
```

Since we setup the span processor to use a `ConsoleSpanExporter`, our output will be sent to the console. This is useful for dev work and we will later take a look at more production workflows. Here is what a sample export would look like:

```bash
{
    "name": "openai.create with gpt-3.5-turbo",
    "context": {
        "trace_id": "0xf27fe6643f5731d4ccb7774c2c14912f",
        "span_id": "0x6edaeefdac4dc041",
        "trace_state": "[]"
    },
    "kind": "SpanKind.CLIENT",
    "parent_id": "0xc414affa9131b6a4",
    "start_time": "2024-06-12T22:00:22.301172Z",
    "end_time": "2024-06-12T22:00:25.037171Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "async": false,
        "gen_ai.system": "openai",
        "gen_ai.request.model": "gpt-3.5-turbo",
        "gen_ai.response.model": "gpt-3.5-turbo-0125",
        "gen_ai.response.id": "chatcmpl-9ZQIy7uIDY5FLoFxwxDsJuUzdbRhj",
        "gen_ai.response.finish_reasons": [
            "tool_calls"
        ],
        "gen_ai.usage.completion_tokens": 26,
        "gen_ai.usage.prompt_tokens": 114
    },
    "events": [
        {
            "name": "gen_ai.content.prompt",
            "timestamp": "2024-06-12T22:00:22.301195Z",
            "attributes": {
                "gen_ai.prompt": "null"
            }
        },
        {
            "name": "gen_ai.content.completion",
            "timestamp": "2024-06-12T22:00:25.037129Z",
            "attributes": {
                "gen_ai.completion": "[{\"role\": \"assistant\", \"tool_calls\": [{\"function\": {\"arguments\": \"{\\\"description\\\":\\\"Submit quarterly report\\\",\\\"due_date\\\":\\\"next Friday\\\",\\\"priority\\\":\\\"high\\\"}\", \"name\": \"TaskDetails\"}}]}]"
            }
        }
    ],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.22.0",
            "service.name": "YOUR_SERVICE_NAME"
        },
        "schema_url": ""
    }
}
{
    "name": "TaskExtractor.extract",
    "context": {
        "trace_id": "0xf27fe6643f5731d4ccb7774c2c14912f",
        "span_id": "0xc414affa9131b6a4",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-06-12T22:00:22.292563Z",
    "end_time": "2024-06-12T22:00:25.037683Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "prompt_template": "\n    Extract the task details from the following task:\n    {task}\n    ",
        "configuration": "{\"llm_ops\": [\"mirascope_otel_decorator\"], \"client_wrappers\": []}",
        "tags": [],
        "_provider": "openai",
        "call_params": "{\"model\": \"gpt-3.5-turbo\", \"tools\": null, \"frequency_penalty\": null, \"logit_bias\": null, \"logprobs\": null, \"max_tokens\": null, \"n\": null, \"presence_penalty\": null, \"response_format\": null, \"seed\": null, \"stop\": null, \"temperature\": null, \"tool_choice\": null, \"top_logprobs\": null, \"top_p\": null, \"user\": null, \"extra_headers\": null, \"extra_query\": null, \"extra_body\": null, \"timeout\": null}",
        "base_url": "",
        "extract_schema": "TaskDetails",
        "task": "Submit quarterly report by next Friday. Task is high priority.",
        "response": "{'description': 'Submit quarterly report', 'due_date': 'next Friday', 'priority': 'high'}"
    },
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.22.0",
            "service.name": "YOUR_SERVICE_NAME"
        },
        "schema_url": ""
    }
}
description='Submit quarterly report' due_date='next Friday' priority='high'
```

The attributes and events match the specs described by [OpenTelemetry Semantic Conventions for LLM requests](https://opentelemetry.io/docs/specs/semconv/gen-ai/llm-spans/).

### Sending to an observability tool

Now, we want to send to an actual observability tool so that we can monitor our traces. There are many observability tools out there, but the majority of them can collect OpenTelemetry data. You can pass in `processors` as an argument of `configure()` so that you can send to an observability tool:

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from mirascope.otel import configure

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

You should refer to your observability tool's documentation to find the endpoint.

## Integrations

But of course if there is an integration that you would like [let us know](https://github.com/Mirascope/mirascope/issues) what observability backends you would like for us to integrate out-of-the-box.
