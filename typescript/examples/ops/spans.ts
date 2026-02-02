/**
 * Span and context propagation example.
 *
 * This example demonstrates explicit span creation and context propagation
 * for distributed tracing across service boundaries.
 */
import { ops } from "mirascope";

// Configure tracing
ops.configure({
  apiKey: process.env.MIRASCOPE_API_KEY,
});

// Create explicit spans for custom operations
await ops.span("data-processing", async (span) => {
  span.info("Starting data processing");

  // Set custom attributes
  span.set({
    "app.batch_size": 100,
    "app.source": "user-upload",
  });

  // Add events with logging methods
  span.debug("Validating input data");

  // Simulate processing
  const data = Array.from({ length: 100 }, (_, i) => ({ id: i, value: i * 2 }));

  span.info("Processing complete", { records_processed: data.length });

  return data;
});

// Nested spans
await ops.span("parent-operation", async (parentSpan) => {
  parentSpan.info("Starting parent operation");

  await ops.span("child-operation-1", async (childSpan) => {
    childSpan.info("Doing child work 1");
  });

  await ops.span("child-operation-2", async (childSpan) => {
    childSpan.info("Doing child work 2");
  });

  parentSpan.info("Parent operation complete");
});

// Context propagation for distributed tracing
// Inject context into outgoing HTTP headers
const outgoingHeaders: Record<string, string> = {};
ops.injectContext(outgoingHeaders);
console.log("Outgoing headers:", outgoingHeaders);
// Headers now contain traceparent (W3C) or other format depending on config

// On the receiving side, extract and use the context
// This links the receiving service's traces to the caller's trace
const incomingHeaders = {
  traceparent: "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
};

await ops.propagatedContext(incomingHeaders, async () => {
  // Any spans created here will be children of the incoming trace
  await ops.span("downstream-operation", async (span) => {
    span.info("Processing in downstream service");
  });
});

// Extract session ID from headers (for session propagation)
const sessionHeaders = {
  "Mirascope-Session-Id": "user-123-session-456",
};
const sessionId = ops.extractSessionId(sessionHeaders);
console.log("Extracted session ID:", sessionId);

// Use session with extracted ID
if (sessionId) {
  await ops.session({ id: sessionId }, async () => {
    console.log("Continuing session from upstream service");
    console.log("Current session:", ops.currentSession());
  });
}
