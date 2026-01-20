import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import { CloudLayout } from "@/app/components/cloud-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";

const CODE_EXAMPLE = `import marimo as mo
from datetime import datetime, timedelta
from mirascope import api

client = api.Mirascope()

# Search traces for a specific function
traces = client.traces.search(
    function_id="your-function-uuid",
    start_time=(datetime.now() - timedelta(days=7)).isoformat(),
    end_time=datetime.now().isoformat(),
    limit=100,
)

# Display traces as a Marimo table
mo.ui.table([
    {
        "trace_id": span.trace_id,
        "span_id": span.span_id,
        "name": span.name,
        "model": span.model,
        "tokens": span.total_tokens,
        "duration_ms": span.duration_ms,
        "start_time": span.start_time,
    }
    for span in traces.spans
])`;

const ANNOTATION_EXAMPLE = `# Annotate a specific trace (use trace_id from table above)
client.annotations.create(
    otel_trace_id="abc123...",  # trace_id from the table
    otel_span_id="def456...",   # span_id from the table
    label="pass",  # or "fail"
    reasoning="Response was accurate and helpful",
    tags=["reviewed", "production"],
    metadata={"reviewer": "human", "score": 0.95},
)`;

function AnnotationQueuePage() {
  return (
    <Protected>
      <CloudLayout>
        <div className="p-6 max-w-4xl">
          <h1 className="text-2xl font-semibold mb-2">Annotation Queue</h1>
          <div className="bg-muted/50 border rounded-lg px-4 pt-4 pb-2 mb-6">
            <p className="text-muted-foreground mb-4">
              While we build the annotation queue UI, you can annotate traces
              programmatically using our Python SDK. We recommend using{" "}
              <a
                href="https://marimo.io"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                Marimo notebooks
              </a>{" "}
              for interactive annotation and evaluation workflows.
            </p>

            <h3 className="text-base font-medium mb-2">
              1. Fetch and display traces for a function
            </h3>
            <CodeBlock code={CODE_EXAMPLE} language="python" className="mb-6" />

            <h3 className="text-base font-medium mb-2">2. Annotate a trace</h3>
            <CodeBlock code={ANNOTATION_EXAMPLE} language="python" />
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/annotation-queue")({
  component: AnnotationQueuePage,
});
