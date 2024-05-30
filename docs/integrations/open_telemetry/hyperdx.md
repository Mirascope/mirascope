# HyperDX

Mirascope provides out-of-the-box integration with [HyperDX](https://www.hyperdx.io).

## The Setup

The setup is largely the same as our [OpenTelemetry integration](https://docs.mirascope.io/latest/integrations/open_telemetry/), so check that out if you have not already.

```python
import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)
from mirascope.openai import OpenAICall
from mirascope.otel import configure
from mirascope.otel.hyperdx import with_hyperdx

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

OBSERVABILITY_TOOL_ENDPOINT = "https://in-otel.hyperdx.io"

# If you do not call configure, it will be automatically called like this for the first time
configure(
    processors=[
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=f"{OBSERVABILITY_TOOL_ENDPOINT}/v1/traces",
                headers={"authorization": os.getenv("HYPERDX_API_KEY")},
            )
        )
    ]
)

@with_hyperdx
class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call() # this will be logged to HyperDX
print(response.content)
```

Now after the one time setup of `configure`, you can add the `@with_hyperdx` decorator to collect traces.
