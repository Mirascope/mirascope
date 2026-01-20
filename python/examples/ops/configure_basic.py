from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from mirascope import ops

# Create a tracer provider with console export for demonstration
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# Configure ops with the tracer provider
ops.configure(tracer_provider=provider)
