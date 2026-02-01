/**
 * Stub OTLP exporter for Mirascope Cloud.
 * Full implementation will be added in PR 5.
 */

import type { SpanExporter, ReadableSpan } from "@opentelemetry/sdk-trace-node";

import { ExportResultCode } from "@opentelemetry/core";

import type { MirascopeClient } from "@/api/client";

/**
 * Exports spans to Mirascope Cloud.
 *
 * This is a stub implementation that accepts but does not actually export spans.
 * The full implementation with retry logic and OTLP format conversion will be
 * added in a future PR.
 */
export class MirascopeOTLPExporter implements SpanExporter {
  private _shutdown = false;

  constructor(private readonly _client: MirascopeClient) {}

  export(
    spans: ReadableSpan[],
    resultCallback: (result: { code: ExportResultCode; error?: Error }) => void,
  ): void {
    if (this._shutdown || spans.length === 0) {
      resultCallback({ code: ExportResultCode.SUCCESS });
      return;
    }
    // Stub: just succeed for now, full implementation in future PR
    resultCallback({ code: ExportResultCode.SUCCESS });
  }

  shutdown(): Promise<void> {
    this._shutdown = true;
    return Promise.resolve();
  }

  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}
