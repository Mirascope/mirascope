from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import configure, with_otel

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


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@with_otel()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
