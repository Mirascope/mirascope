from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from mirascope import ops

# Create OTLP exporter (sends to localhost:4317 by default)
exporter = OTLPSpanExporter()

# Create tracer provider with batch processing for production use
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(exporter))

# Configure ops
ops.configure(tracer_provider=provider)
