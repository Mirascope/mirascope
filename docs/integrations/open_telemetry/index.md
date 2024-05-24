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
        "trace_id": "0x7d3b690ea168b631fa24846f7cfeae71",
        "span_id": "0x6ad9e80426ec06f4",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0x8f7cf8f30696ec7f",
    "start_time": "2024-05-24T00:51:29.123175Z",
    "end_time": "2024-05-24T00:51:49.712021Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "async": false,
        "request_data": "{\"messages\": [{\"role\": \"user\", \"content\": \"Extract the task details from the following task:\\nSubmit quarterly report by next Friday. Task is high priority.\"}], \"stream\": false, \"model\": \"gpt-3.5-turbo\", \"tools\": [{\"type\": \"function\", \"function\": {\"name\": \"TaskDetails\", \"description\": \"Correctly formatted and typed parameters extracted from the completion. Must include required parameters and may exclude optional parameters unless present in the text.\", \"parameters\": {\"properties\": {\"description\": {\"title\": \"Description\", \"type\": \"string\"}, \"due_date\": {\"title\": \"Due Date\", \"type\": \"string\"}, \"priority\": {\"enum\": [\"low\", \"normal\", \"high\"], \"title\": \"Priority\", \"type\": \"string\"}}, \"required\": [\"description\", \"due_date\", \"priority\"], \"type\": \"object\"}}}]}",
        "response_data": "{\"message\": {\"role\": \"assistant\", \"tool_calls\": [{\"function\": {\"arguments\": \"{\\\"description\\\":\\\"Submit quarterly report\\\",\\\"due_date\\\":\\\"next Friday\\\",\\\"priority\\\":\\\"high\\\"}\", \"name\": \"TaskDetails\"}}]}}"
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
{
    "name": "TaskExtractor.extract",
    "context": {
        "trace_id": "0x7d3b690ea168b631fa24846f7cfeae71",
        "span_id": "0x8f7cf8f30696ec7f",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-05-24T00:51:29.113405Z",
    "end_time": "2024-05-24T00:51:49.712510Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "prompt_template": "\n    Extract the task details from the following task:\n    {task}\n    ",
        "_provider": "openai",
        "tags": [],
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
