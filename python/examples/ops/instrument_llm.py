from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from mirascope import llm, ops

# Set up OpenTelemetry tracing with a console exporter
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

# Configure tracing with the provider
ops.configure(tracer_provider=provider)

# Enable automatic LLM instrumentation for Gen AI spans
ops.instrument_llm()

# Now all Model calls are automatically traced with Gen AI semantic conventions
model = llm.model("openai/gpt-4o-mini")
response = model.call("What is the capital of France?")
print(response.text())

# Disable instrumentation when done
ops.uninstrument_llm()
