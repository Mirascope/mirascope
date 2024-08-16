"""Mirascope x HyperDX Integration."""

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from mirascope.integrations.otel._utils import configure
from mirascope.integrations.otel._with_otel import with_otel


def with_hyperdx():
    """Decorator to wrap a function with hyperdx.

    Example:

    ```python
    import os

    from mirascope.core import anthropic, prompt_template
    from mirascope.integrations.otel import with_hyperdx

    os.environ["HYPERDX_API_KEY"] = "YOUR_API_KEY"


    def format_book(title: str, author: str):
        return f"{title} by {author}"


    @with_hyperdx()
    @anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
    @prompt_template("Recommend a {genre} book.")
    def recommend_book(genre: str):
        ...


    print(recommend_book("fantasy"))
    ```
    """
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        configure(
            processors=[
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint="https://in-otel.hyperdx.io/v1/traces",
                        headers={"authorization": os.getenv("HYPERDX_API_KEY", "")},
                    )
                )
            ]
        )
    return with_otel()
