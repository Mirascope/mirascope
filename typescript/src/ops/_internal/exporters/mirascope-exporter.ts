/**
 * OTLP exporter for Mirascope Cloud.
 *
 * Exports OpenTelemetry spans to Mirascope Cloud with retry logic
 * and proper OTLP format conversion.
 */

import type { SpanExporter, ReadableSpan } from "@opentelemetry/sdk-trace-node";

import { SpanKind, SpanStatusCode } from "@opentelemetry/api";
import { ExportResultCode } from "@opentelemetry/core";

import type { MirascopeClient } from "@/api/client";

/**
 * OTLP attribute value format.
 * Note: intValue is a string to match the API spec (large integers).
 */
interface OtlpAttributeValue {
  stringValue?: string;
  intValue?: string;
  doubleValue?: number;
  boolValue?: boolean;
  arrayValue?: { values: OtlpAttributeValue[] };
}

/**
 * OTLP attribute format.
 */
interface OtlpAttribute {
  key: string;
  value: OtlpAttributeValue;
}

/**
 * OTLP event format.
 */
interface OtlpEvent {
  name: string;
  timeUnixNano: string;
  attributes: OtlpAttribute[];
}

/**
 * OTLP span format.
 */
interface OtlpSpan {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  name: string;
  kind: number;
  startTimeUnixNano: string;
  endTimeUnixNano: string;
  attributes: OtlpAttribute[];
  events: OtlpEvent[];
  status: { code: number; message?: string };
}

/**
 * OTLP resource spans format.
 */
interface OtlpResourceSpans {
  resource: {
    attributes: OtlpAttribute[];
  };
  scopeSpans: Array<{
    scope: { name: string; version?: string };
    spans: OtlpSpan[];
  }>;
}

/**
 * Convert a value to OTLP attribute value format.
 */
function toOtlpAttributeValue(value: unknown): OtlpAttributeValue {
  if (typeof value === "string") {
    return { stringValue: value };
  }
  if (typeof value === "number") {
    if (Number.isInteger(value)) {
      return { intValue: String(value) };
    }
    return { doubleValue: value };
  }
  if (typeof value === "boolean") {
    return { boolValue: value };
  }
  /* v8 ignore start - v8 coverage artifact at block boundary + fallback for unsupported types */
  if (Array.isArray(value)) {
    return {
      arrayValue: {
        values: value.map((v) => toOtlpAttributeValue(v)),
      },
    };
  }
  // Fallback: convert to string (for unsupported types)
  return { stringValue: String(value) };
  /* v8 ignore end */
}

/**
 * Convert span kind to OTLP span kind number.
 */
function toOtlpSpanKind(kind: SpanKind): number {
  switch (kind) {
    case SpanKind.INTERNAL:
      return 1;
    case SpanKind.SERVER:
      return 2;
    case SpanKind.CLIENT:
      return 3;
    case SpanKind.PRODUCER:
      return 4;
    case SpanKind.CONSUMER:
      return 5;
    default:
      return 0; // UNSPECIFIED
  }
}

/**
 * Convert span status to OTLP status code.
 */
function toOtlpStatusCode(code: SpanStatusCode): number {
  switch (code) {
    case SpanStatusCode.OK:
      return 1;
    case SpanStatusCode.ERROR:
      return 2;
    default:
      return 0; // UNSET
  }
}

/**
 * Convert HrTime to nanoseconds string.
 */
function hrTimeToNanos(hrTime: [number, number]): string {
  const nanos = BigInt(hrTime[0]) * BigInt(1e9) + BigInt(hrTime[1]);
  return nanos.toString();
}

/**
 * Exports spans to Mirascope Cloud.
 *
 * Converts OpenTelemetry spans to OTLP format and sends them to the
 * Mirascope Cloud traces endpoint with exponential backoff retry.
 *
 * @example
 * ```typescript
 * const client = new MirascopeClient({ apiKey: 'your-key' });
 * const exporter = new MirascopeOTLPExporter(client);
 *
 * // Use with TracerProvider
 * const provider = new TracerProvider();
 * provider.addSpanProcessor(new BatchSpanProcessor(exporter));
 * ```
 */
export class MirascopeOTLPExporter implements SpanExporter {
  private _shutdown = false;

  /**
   * Create a new MirascopeOTLPExporter.
   *
   * @param _client - The Mirascope API client
   * @param _maxRetryAttempts - Maximum number of retry attempts (default: 3)
   * @param _initialDelayMs - Initial delay between retries in ms (default: 100)
   * @param _maxDelayMs - Maximum delay between retries in ms (default: 5000)
   */
  constructor(
    private readonly _client: MirascopeClient,
    private readonly _maxRetryAttempts = 3,
    private readonly _initialDelayMs = 100,
    private readonly _maxDelayMs = 5000,
  ) {}

  /**
   * Export spans to Mirascope Cloud.
   *
   * @param spans - The spans to export
   * @param resultCallback - Callback to receive the export result
   */
  export(
    spans: ReadableSpan[],
    resultCallback: (result: { code: ExportResultCode; error?: Error }) => void,
  ): void {
    this.doExport(spans, resultCallback);
  }

  private async doExport(
    spans: ReadableSpan[],
    resultCallback: (result: { code: ExportResultCode; error?: Error }) => void,
  ): Promise<void> {
    if (this._shutdown || spans.length === 0) {
      resultCallback({ code: ExportResultCode.SUCCESS });
      return;
    }

    let delay = this._initialDelayMs;
    let lastError: Error | undefined;

    for (let attempt = 0; attempt < this._maxRetryAttempts; attempt++) {
      if (attempt > 0) {
        await this.sleep(delay);
        delay = Math.min(delay * 2, this._maxDelayMs);
      }

      try {
        const resourceSpans = this.convertSpansToOTLP(spans);
        await this._client.traces.create({ resourceSpans });
        resultCallback({ code: ExportResultCode.SUCCESS });
        return;
      } catch (error) {
        lastError = error instanceof Error ? error : new Error(String(error));
        // Continue to next retry attempt
      }
    }

    resultCallback({ code: ExportResultCode.FAILED, error: lastError });
  }

  /**
   * Convert OpenTelemetry spans to OTLP resource spans format.
   */
  private convertSpansToOTLP(spans: ReadableSpan[]): OtlpResourceSpans[] {
    // Group spans by resource and scope
    const resourceMap = new Map<string, Map<string, ReadableSpan[]>>();

    for (const span of spans) {
      const resourceKey = JSON.stringify(span.resource.attributes);
      const scopeKey = `${span.instrumentationScope.name}:${span.instrumentationScope.version ?? ""}`;

      if (!resourceMap.has(resourceKey)) {
        resourceMap.set(resourceKey, new Map());
      }
      const scopeMap = resourceMap.get(resourceKey)!;

      if (!scopeMap.has(scopeKey)) {
        scopeMap.set(scopeKey, []);
      }
      scopeMap.get(scopeKey)!.push(span);
    }

    const resourceSpans: OtlpResourceSpans[] = [];

    for (const [, scopeMap] of resourceMap) {
      const firstSpan = spans[0]!;
      const resourceAttributes: OtlpAttribute[] = [];

      for (const [key, value] of Object.entries(
        firstSpan.resource.attributes,
      )) {
        resourceAttributes.push({
          key,
          value: toOtlpAttributeValue(value),
        });
      }

      const scopeSpans: OtlpResourceSpans["scopeSpans"] = [];

      for (const [, spanList] of scopeMap) {
        const firstScopeSpan = spanList[0]!;
        scopeSpans.push({
          scope: {
            name: firstScopeSpan.instrumentationScope.name,
            version: firstScopeSpan.instrumentationScope.version,
          },
          spans: spanList.map((span) => this.convertSpan(span)),
        });
      }

      resourceSpans.push({
        resource: { attributes: resourceAttributes },
        scopeSpans,
      });
    }

    return resourceSpans;
  }

  /**
   * Convert a single OpenTelemetry span to OTLP format.
   */
  private convertSpan(span: ReadableSpan): OtlpSpan {
    const attributes: OtlpAttribute[] = [];
    for (const [key, value] of Object.entries(span.attributes)) {
      attributes.push({
        key,
        value: toOtlpAttributeValue(value),
      });
    }

    const events: OtlpEvent[] = span.events.map((event) => {
      const eventAttrs: OtlpAttribute[] = [];
      if (event.attributes) {
        for (const [key, value] of Object.entries(event.attributes)) {
          eventAttrs.push({
            key,
            value: toOtlpAttributeValue(value),
          });
        }
      }
      return {
        name: event.name,
        timeUnixNano: hrTimeToNanos(event.time),
        attributes: eventAttrs,
      };
    });

    const otlpSpan: OtlpSpan = {
      traceId: span.spanContext().traceId,
      spanId: span.spanContext().spanId,
      name: span.name,
      kind: toOtlpSpanKind(span.kind),
      startTimeUnixNano: hrTimeToNanos(span.startTime),
      endTimeUnixNano: hrTimeToNanos(span.endTime),
      attributes,
      events,
      status: {
        code: toOtlpStatusCode(span.status.code),
        message: span.status.message,
      },
    };

    const parentSpanId = span.parentSpanContext?.spanId;
    if (parentSpanId) {
      otlpSpan.parentSpanId = parentSpanId;
    }

    return otlpSpan;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Shutdown the exporter.
   */
  shutdown(): Promise<void> {
    this._shutdown = true;
    return Promise.resolve();
  }

  /**
   * Force flush any pending spans.
   */
  forceFlush(): Promise<void> {
    return Promise.resolve();
  }
}
