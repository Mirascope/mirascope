import { useState, type ReactNode } from "react";
import { AlertCircle, Code, FileCode, X } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import { Button } from "@/app/components/ui/button";
import { JsonView } from "@/app/components/json-view";
import { CodeBlock } from "@/app/components/ai-elements/code-block";
import { safeParseJSON } from "@/app/lib/utils";
import { formatDuration, formatTimestamp } from "@/app/lib/traces/formatting";
import { KNOWN_LEVELS, getLevelStyles } from "@/app/lib/traces/event-styles";
import type { SpanDetail, SpanSearchResult } from "@/api/traces-search.schemas";
import type { FunctionResponse } from "@/api/functions.schemas";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/app/components/ai-elements/message";
import {
  Tool,
  ToolHeader,
  ToolContent,
  ToolInput,
  ToolOutput,
} from "@/app/components/ai-elements/tool";
import {
  Reasoning,
  ReasoningTrigger,
  ReasoningContent,
} from "@/app/components/ai-elements/reasoning";

interface SpanDetailPanelProps {
  span: SpanDetail | SpanSearchResult | null;
  functionData?: FunctionResponse | null;
  onClose: () => void;
}

/** Type guard to check if span has detailed data (attributes field) */
function isSpanDetail(span: SpanDetail | SpanSearchResult): span is SpanDetail {
  return "attributes" in span;
}

/** Extract GenAI messages (handles various formats: array, JSON string, plain string) */
function extractGenAiMessages(
  attributes: Record<string, unknown> | null,
  key: string,
): unknown[] | null {
  if (!attributes) return null;
  const value = attributes[key];
  if (value === undefined || value === null) return null;

  // Already an array
  if (Array.isArray(value)) return value as unknown[];

  // String - could be JSON or plain text
  if (typeof value === "string") {
    const trimmed = value.trim();
    // Try parsing as JSON
    if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
      const parsed = safeParseJSON(trimmed);
      if (Array.isArray(parsed)) return parsed;
      // Single JSON object - wrap in array
      if (parsed && typeof parsed === "object") return [parsed];
    }
    // Plain string - treat as content
    if (trimmed) return [{ role: "user", content: trimmed }];
  }

  // Object - wrap in array
  if (typeof value === "object") return [value];

  return null;
}

/** Extract trace function arguments (object with arg names as keys) */
function extractTraceArgs(
  attributes: Record<string, unknown> | null,
): Record<string, unknown> | null {
  if (!attributes) return null;
  const argValues = attributes["mirascope.trace.arg_values"];
  if (!argValues) return null;
  const parsed =
    typeof argValues === "string" ? safeParseJSON(argValues) : argValues;
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
    return parsed as Record<string, unknown>;
  }
  return null;
}

/** Extract trace function output (raw value) */
function extractTraceOutput(
  attributes: Record<string, unknown> | null,
): unknown {
  if (!attributes) return undefined;
  const traceOutput = attributes["mirascope.trace.output"];
  if (traceOutput === undefined) return undefined;
  if (typeof traceOutput === "string") {
    return safeParseJSON(traceOutput) ?? traceOutput;
  }
  return traceOutput;
}

/** Check if this is a GenAI/LLM span (has actual gen_ai content) */
function isGenAiSpan(attributes: Record<string, unknown> | null): boolean {
  if (!attributes) return false;
  // Check for presence of gen_ai attributes with actual content (support both old and new key formats)
  const hasInputMessages =
    attributes["gen_ai.input.messages"] != null ||
    attributes["gen_ai.input_messages"] != null;
  const hasOutputMessages =
    attributes["gen_ai.output.messages"] != null ||
    attributes["gen_ai.output_messages"] != null;
  const hasSystem = attributes["gen_ai.system"] != null;
  const hasModel = attributes["gen_ai.request.model"] != null;
  return hasInputMessages || hasOutputMessages || hasSystem || hasModel;
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div>
      <h4 className="mb-2 text-sm font-medium">{title}</h4>
      {children}
    </div>
  );
}

/** Part type for tool calls */
type ToolCallPart = {
  type: "tool_call";
  id?: string;
  tool_call_id?: string;
  name: string;
  arguments?: unknown;
};

/** Part type for tool responses */
type ToolResponsePart = {
  type: "tool_call_response";
  id?: string;
  tool_call_id?: string;
  response?: unknown;
  content?: unknown;
};

/** Combined tool with both call and response */
type CombinedTool = {
  call: ToolCallPart;
  response?: ToolResponsePart;
};

/** Get the tool call ID from a part, checking multiple possible field names */
function getToolId(part: unknown): string | undefined {
  if (!part || typeof part !== "object") return undefined;
  const p = part as { id?: string; tool_call_id?: string };
  return p.id ?? p.tool_call_id;
}

/** Process parts to combine tool calls with their responses */
function processPartsWithToolMatching(parts: unknown[]): {
  processedParts: unknown[];
  matchedResponseIndices: Set<number>;
} {
  // Collect all tool calls and responses with their indices
  const toolCalls: Array<{ part: ToolCallPart; index: number; id?: string }> =
    [];
  const toolResponses: Array<{
    part: ToolResponsePart;
    index: number;
    id?: string;
  }> = [];

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!part || typeof part !== "object") continue;
    const p = part as { type?: string };
    const toolId = getToolId(part);

    if (p.type === "tool_call") {
      toolCalls.push({ part: part as ToolCallPart, index: i, id: toolId });
    } else if (p.type === "tool_call_response") {
      toolResponses.push({
        part: part as ToolResponsePart,
        index: i,
        id: toolId,
      });
    }
  }

  // Build a map of tool call index -> matched response
  const callToResponse: Map<number, ToolResponsePart> = new Map();
  const matchedResponseIndices = new Set<number>();
  const matchedCallIndices = new Set<number>();

  // Strategy 1: Match by ID (when both have matching IDs)
  for (const call of toolCalls) {
    if (!call.id) continue;
    const response = toolResponses.find(
      (r) => r.id === call.id && !matchedResponseIndices.has(r.index),
    );
    if (response) {
      callToResponse.set(call.index, response.part);
      matchedResponseIndices.add(response.index);
      matchedCallIndices.add(call.index);
    }
  }

  // Strategy 2: Match ALL remaining unmatched calls to responses by position
  // This handles cases where IDs don't match or are missing on one/both sides
  const unmatchedCalls = toolCalls.filter(
    (c) => !matchedCallIndices.has(c.index),
  );
  const unmatchedResponses = toolResponses.filter(
    (r) => !matchedResponseIndices.has(r.index),
  );

  for (
    let i = 0;
    i < Math.min(unmatchedCalls.length, unmatchedResponses.length);
    i++
  ) {
    callToResponse.set(unmatchedCalls[i].index, unmatchedResponses[i].part);
    matchedResponseIndices.add(unmatchedResponses[i].index);
  }

  // Build processed parts list
  const processedParts: unknown[] = [];

  for (let i = 0; i < parts.length; i++) {
    const part = parts[i];
    if (!part || typeof part !== "object") {
      processedParts.push(part);
      continue;
    }
    const p = part as { type?: string };

    if (p.type === "tool_call") {
      const response = callToResponse.get(i);
      // Add as combined tool (with or without response)
      processedParts.push({
        _combined: true,
        call: part,
        response: response,
      } as CombinedTool & { _combined: true });
    } else if (p.type === "tool_call_response") {
      // Skip if matched with a call
      if (matchedResponseIndices.has(i)) continue;
      // Orphan response - still render it
      processedParts.push(part);
    } else {
      // All other parts pass through
      processedParts.push(part);
    }
  }

  return { processedParts, matchedResponseIndices };
}

/** Render a single message part (text, tool call, etc.) */
function renderPart(part: unknown, idx: number): ReactNode {
  if (!part || typeof part !== "object") {
    return (
      <p key={idx} className="text-sm">
        {String(part)}
      </p>
    );
  }

  // Check for combined tool (call + response)
  const combined = part as {
    _combined?: boolean;
    call?: ToolCallPart;
    response?: ToolResponsePart;
  };
  if (combined._combined && combined.call) {
    const { call, response } = combined;
    // Get output from response or content field
    const outputData = response
      ? (response.response ?? response.content)
      : undefined;
    return (
      <Tool key={idx} defaultOpen={false}>
        <ToolHeader
          title={call.name}
          type="tool-call"
          state={
            outputData !== undefined ? "output-available" : "input-available"
          }
        />
        <ToolContent>
          <ToolInput input={call.arguments} />
          {outputData !== undefined && (
            <ToolOutput output={outputData} errorText={undefined} />
          )}
        </ToolContent>
      </Tool>
    );
  }

  const p = part as {
    type?: string;
    text?: string;
    content?: unknown;
    name?: string;
    arguments?: unknown;
    response?: unknown;
    id?: string;
    tool_call_id?: string;
  };

  // Text part (new format: type="text" with content field)
  if (p.type === "text" && typeof p.content === "string") {
    return <MessageResponse key={idx}>{p.content}</MessageResponse>;
  }

  // Text part (old format: type="text" with text field)
  if (p.type === "text" && p.text) {
    return <MessageResponse key={idx}>{p.text}</MessageResponse>;
  }

  // Standalone tool call (no matching response found)
  if (p.type === "tool_call" && p.name) {
    return (
      <Tool key={idx} defaultOpen={false}>
        <ToolHeader title={p.name} type="tool-call" state="output-available" />
        <ToolContent>
          <ToolInput input={p.arguments} />
        </ToolContent>
      </Tool>
    );
  }

  // Orphan tool response (no matching call found)
  if (p.type === "tool_call_response") {
    const outputData = p.response ?? p.content;
    return (
      <Tool key={idx} defaultOpen={false}>
        <ToolHeader
          title="Tool Response"
          type="tool-result"
          state="output-available"
        />
        <ToolContent>
          <ToolOutput output={outputData} errorText={undefined} />
        </ToolContent>
      </Tool>
    );
  }

  // Reasoning part
  if (p.type === "reasoning" && typeof p.content === "string") {
    return (
      <Reasoning key={idx} defaultOpen={false}>
        <ReasoningTrigger />
        <ReasoningContent>{p.content}</ReasoningContent>
      </Reasoning>
    );
  }

  // Fallback for other types
  return <JsonView key={idx} value={part} />;
}

/** Pre-process messages to combine tool calls with their responses across messages */
function combineMessagesWithToolResponses(messages: unknown[]): unknown[] {
  // First pass: collect all tool responses by ID from:
  // 1. role: "tool" messages (legacy format)
  // 2. tool_call_response parts in any message (OTEL Gen AI spec format)
  const toolResponsesById: Map<string, unknown> = new Map();
  const toolResponsesByName: Map<string, unknown> = new Map();

  for (const msg of messages) {
    if (!msg || typeof msg !== "object") continue;
    const m = msg as {
      role?: string;
      parts?: unknown[];
      content?: unknown;
      tool_call_id?: string;
      name?: string;
    };

    // Handle role: "tool" messages (legacy format)
    if (m.role === "tool") {
      const toolId = m.tool_call_id ?? getToolId(m);
      const toolName = m.name;
      const responseContent = m.content ?? m.parts;

      if (toolId) {
        toolResponsesById.set(toolId, responseContent);
      } else if (toolName) {
        toolResponsesByName.set(toolName, responseContent);
      }
      continue;
    }

    // Handle tool_call_response parts in any message (OTEL Gen AI spec format)
    if (Array.isArray(m.parts)) {
      for (const part of m.parts) {
        if (!part || typeof part !== "object") continue;
        const p = part as {
          type?: string;
          id?: string;
          tool_call_id?: string;
          response?: unknown;
          content?: unknown;
        };
        if (p.type === "tool_call_response") {
          const toolId = p.id ?? p.tool_call_id;
          const responseContent = p.response ?? p.content;
          if (toolId) {
            toolResponsesById.set(toolId, responseContent);
          }
        }
      }
    }
  }

  // If no tool responses found, return original
  if (toolResponsesById.size === 0 && toolResponsesByName.size === 0) {
    return messages;
  }

  // Second pass: inject tool responses into tool calls and filter out tool_call_response parts
  const result: unknown[] = [];

  for (const msg of messages) {
    if (!msg || typeof msg !== "object") {
      result.push(msg);
      continue;
    }
    const m = msg as { role?: string; parts?: unknown[]; content?: unknown };

    // Skip tool-role messages (we've already extracted their content)
    if (m.role === "tool") continue;

    // For messages with parts array
    if (m.parts && Array.isArray(m.parts)) {
      // Filter out tool_call_response parts (they've been extracted for merging)
      const filteredParts = m.parts.filter((part) => {
        if (!part || typeof part !== "object") return true;
        const p = part as { type?: string };
        return p.type !== "tool_call_response";
      });

      // Skip message if all parts were tool_call_response
      if (filteredParts.length === 0) continue;

      // Inject tool responses into tool_call parts
      const newParts = filteredParts.map((part) => {
        if (!part || typeof part !== "object") return part;
        const p = part as {
          type?: string;
          id?: string;
          tool_call_id?: string;
          name?: string;
        };

        if (p.type === "tool_call") {
          const toolId = p.id ?? p.tool_call_id;
          const toolName = p.name;

          // Try to find matching response
          let responseContent: unknown = undefined;
          if (toolId && toolResponsesById.has(toolId)) {
            responseContent = toolResponsesById.get(toolId);
          } else if (toolName && toolResponsesByName.has(toolName)) {
            responseContent = toolResponsesByName.get(toolName);
          }

          if (responseContent !== undefined) {
            // Return a combined tool with injected response
            return {
              _combined: true,
              call: part,
              response: {
                type: "tool_call_response",
                response: responseContent,
              },
            };
          }
        }
        return part;
      });

      result.push({ ...m, parts: newParts });
    } else {
      result.push(msg);
    }
  }

  return result;
}

/** Render a GenAI message (supports text, tool calls, parts array) */
function MessageCard({ message }: { message: unknown }) {
  if (!message || typeof message !== "object") return null;
  const msg = message as {
    role?: string;
    content?: unknown;
    parts?: unknown[];
  };

  const role = msg.role ?? "unknown";
  const content = msg.content;
  const parts = msg.parts;

  // Skip tool-role messages (they're handled by combining with tool calls)
  if (role === "tool") return null;

  // Handle different content types
  const renderContent = () => {
    // New format: parts array (OpenTelemetry Gen AI semantic conventions)
    if (Array.isArray(parts) && parts.length > 0) {
      const { processedParts } = processPartsWithToolMatching(parts);
      return processedParts.map((part, idx) => renderPart(part, idx));
    }

    // String content - use MessageResponse for markdown rendering
    if (typeof content === "string") {
      return <MessageResponse>{content}</MessageResponse>;
    }

    // Array content (multiple parts: text, tool calls, etc.)
    if (Array.isArray(content)) {
      const { processedParts } = processPartsWithToolMatching(content);
      return processedParts.map((part, idx) => renderPart(part, idx));
    }

    // Object content (fallback)
    if (content && typeof content === "object") {
      return <JsonView value={content} />;
    }

    return null;
  };

  // System role gets distinct styling
  if (role === "system") {
    return (
      <div className="rounded-lg border border-dashed border-muted-foreground/30 bg-muted/50 p-3">
        <div className="mb-2 text-xs font-medium text-muted-foreground">
          System
        </div>
        <div className="text-sm">{renderContent()}</div>
      </div>
    );
  }

  // Map role to Message 'from' prop - user on right, assistant on left
  const from = role === "user" ? "user" : "assistant";

  return (
    <Message from={from}>
      <MessageContent>{renderContent()}</MessageContent>
    </Message>
  );
}

export function SpanDetailPanel({
  span,
  functionData,
  onClose,
}: SpanDetailPanelProps) {
  const [showFullCode, setShowFullCode] = useState(false);

  if (!span) return null;

  const hasDetailedData = isSpanDetail(span);
  const attributes = hasDetailedData ? safeParseJSON(span.attributes) : null;
  const attrs = attributes && !Array.isArray(attributes) ? attributes : null;
  const events =
    hasDetailedData && span.events ? safeParseJSON(span.events) : null;

  // Determine span type and extract appropriate data
  const isLlmSpan = isGenAiSpan(attrs);
  // Try both old and new attribute key formats
  const genAiInputMessages =
    extractGenAiMessages(attrs, "gen_ai.input.messages") ??
    extractGenAiMessages(attrs, "gen_ai.input_messages");
  const genAiOutputMessages =
    extractGenAiMessages(attrs, "gen_ai.output.messages") ??
    extractGenAiMessages(attrs, "gen_ai.output_messages");
  const genAiSystemInstructions: unknown[] | null = (() => {
    const raw = attrs?.["gen_ai.system_instructions"];
    if (!raw) return null;
    try {
      const parsed: unknown = typeof raw === "string" ? JSON.parse(raw) : raw;
      return Array.isArray(parsed) ? parsed : null;
    } catch {
      return null;
    }
  })();
  const traceArgs = extractTraceArgs(attrs);
  const traceOutput = extractTraceOutput(attrs);

  // Extract mirascope-specific attributes
  const isMirascopeTrace = attrs?.["mirascope.type"] === "trace";
  const fnQualname = attrs?.["mirascope.fn.qualname"] as string | undefined;
  const fnModule = attrs?.["mirascope.fn.module"] as string | undefined;
  const traceTags = attrs?.["mirascope.trace.tags"] as string[] | undefined;
  const sessionId = attrs?.["mirascope.ops.session.id"] as string | undefined;

  return (
    <div className="flex h-full w-full flex-col rounded-lg border bg-background">
      {/* Header */}
      <div className="flex items-center justify-between border-b px-4 py-3">
        <h3 className="truncate text-lg font-semibold">{span.name}</h3>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClose}
          className="h-8 w-8"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Content - single scrollable area */}
      <div className="min-h-0 flex-1 space-y-6 overflow-y-auto p-4">
        {/* Timing */}
        <Section title="Timing">
          <dl className="grid grid-cols-2 gap-2 text-sm">
            <dt className="text-muted-foreground">Duration</dt>
            <dd>{formatDuration(span.durationMs)}</dd>
            <dt className="text-muted-foreground">Started</dt>
            <dd>{formatTimestamp(span.startTime)}</dd>
          </dl>
        </Section>

        {/* Error (if exists) */}
        {hasDetailedData && span.errorType && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>{span.errorType}</AlertTitle>
            <AlertDescription>{span.errorMessage}</AlertDescription>
          </Alert>
        )}

        {functionData && (
          <Section title="Function">
            <div className="space-y-3">
              <dl className="grid grid-cols-2 gap-2 text-sm">
                <dt className="text-muted-foreground">Name</dt>
                <dd>{functionData.name}</dd>
                <dt className="text-muted-foreground">Version</dt>
                <dd>{functionData.version}</dd>
              </dl>
              {functionData && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      {showFullCode ? (
                        <FileCode className="h-4 w-4" />
                      ) : (
                        <Code className="h-4 w-4" />
                      )}
                      <span>{showFullCode ? "Full Code" : "Signature"}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowFullCode(!showFullCode)}
                      className="h-7 text-xs"
                    >
                      {showFullCode ? "Show Signature" : "Show Full Code"}
                    </Button>
                  </div>
                  <div className="rounded-md border">
                    <CodeBlock
                      code={
                        showFullCode
                          ? functionData.code
                          : functionData.signature
                      }
                      language="python"
                    />
                  </div>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* LLM Metrics (if model exists) */}
        {span.model && (
          <Section title="LLM Details">
            <dl className="grid grid-cols-2 gap-2 text-sm">
              <dt className="text-muted-foreground">Model</dt>
              <dd>{span.model}</dd>
              {hasDetailedData && span.provider && (
                <>
                  <dt className="text-muted-foreground">Provider</dt>
                  <dd>{span.provider}</dd>
                </>
              )}
              {hasDetailedData && span.inputTokens !== null && (
                <>
                  <dt className="text-muted-foreground">Input Tokens</dt>
                  <dd>{span.inputTokens.toLocaleString()}</dd>
                </>
              )}
              {hasDetailedData && span.outputTokens !== null && (
                <>
                  <dt className="text-muted-foreground">Output Tokens</dt>
                  <dd>{span.outputTokens.toLocaleString()}</dd>
                </>
              )}
              {hasDetailedData && span.costUsd !== null && (
                <>
                  <dt className="text-muted-foreground">Cost</dt>
                  <dd>${span.costUsd.toFixed(6)}</dd>
                </>
              )}
            </dl>
          </Section>
        )}

        {/* Input: Trace function arguments */}
        {traceArgs && Object.keys(traceArgs).length > 0 && (
          <Section title="Input">
            <div className="rounded-md border p-3">
              <JsonView value={traceArgs} />
            </div>
          </Section>
        )}

        {/* Combined Messages (for LLM spans) - chat-like view */}
        {isLlmSpan &&
          (genAiSystemInstructions ||
            (genAiInputMessages && genAiInputMessages.length > 0) ||
            (genAiOutputMessages && genAiOutputMessages.length > 0)) && (
            <Section title="Messages">
              <div className="rounded-lg border bg-muted/30 p-4">
                <div className="space-y-3">
                  {/* Combine all messages to match tool calls with responses */}
                  {(() => {
                    const allMessages = [
                      // System instructions as first message
                      ...(genAiSystemInstructions
                        ? [{ role: "system", parts: genAiSystemInstructions }]
                        : []),
                      ...(genAiInputMessages ?? []),
                      ...(genAiOutputMessages ?? []),
                    ];
                    const combined =
                      combineMessagesWithToolResponses(allMessages);
                    return combined.map((msg, idx) => (
                      <MessageCard key={idx} message={msg} />
                    ));
                  })()}
                </div>
              </div>
            </Section>
          )}

        {/* Output: Trace function return value (non-LLM spans) */}
        {traceOutput !== undefined && !isLlmSpan && (
          <Section title="Output">
            <div className="rounded-md border p-3">
              {typeof traceOutput === "string" ? (
                <p className="whitespace-pre-wrap font-sans text-sm">
                  {traceOutput}
                </p>
              ) : (
                <JsonView value={traceOutput as object} />
              )}
            </div>
          </Section>
        )}

        {/* Mirascope Trace Details */}
        {isMirascopeTrace && (fnQualname || fnModule || traceTags) && (
          <Section title="Trace Details">
            <dl className="grid grid-cols-2 gap-2 text-sm">
              {fnQualname && (
                <>
                  <dt className="text-muted-foreground">Function</dt>
                  <dd className="truncate font-mono text-xs">{fnQualname}</dd>
                </>
              )}
              {fnModule && (
                <>
                  <dt className="text-muted-foreground">Module</dt>
                  <dd className="truncate font-mono text-xs">{fnModule}</dd>
                </>
              )}
              {traceTags && traceTags.length > 0 && (
                <>
                  <dt className="text-muted-foreground">Tags</dt>
                  <dd>{traceTags.join(", ")}</dd>
                </>
              )}
            </dl>
          </Section>
        )}

        {/* Session Info */}
        {sessionId && (
          <Section title="Session">
            <p className="truncate font-mono text-xs">{sessionId}</p>
          </Section>
        )}

        {/* Events (e.g., .info() calls) */}
        {Array.isArray(events) && events.length > 0 && (
          <Section title="Events">
            <div className="space-y-2">
              {events.map((rawEvent, idx) => {
                if (!rawEvent || typeof rawEvent !== "object") return null;
                const event = rawEvent as Record<string, unknown>;

                // Extract event name
                const name =
                  typeof event.name === "string" ? event.name : "event";

                // Extract attributes - handle both object and array formats
                let attrs: Record<string, unknown> | null = null;
                if (event.attributes) {
                  if (
                    Array.isArray(event.attributes) &&
                    event.attributes.length > 0
                  ) {
                    // OTLP format: array of {key, value} pairs
                    attrs = {};
                    for (const attr of event.attributes) {
                      if (
                        attr &&
                        typeof attr === "object" &&
                        "key" in attr &&
                        "value" in attr
                      ) {
                        const a = attr as { key: string; value: unknown };
                        // Handle OTLP value wrapper (e.g., {stringValue: "..."})
                        const val = a.value;
                        if (
                          val &&
                          typeof val === "object" &&
                          !Array.isArray(val)
                        ) {
                          const v = val as Record<string, unknown>;
                          attrs[a.key] =
                            v.stringValue ?? v.intValue ?? v.boolValue ?? val;
                        } else {
                          attrs[a.key] = val;
                        }
                      }
                    }
                  } else if (
                    typeof event.attributes === "object" &&
                    !Array.isArray(event.attributes)
                  ) {
                    // Already an object
                    attrs = event.attributes as Record<string, unknown>;
                  }
                }

                const level = attrs?.level;
                const message = attrs?.message;
                const attrLevelStr =
                  typeof level === "string"
                    ? level
                    : level != null
                      ? JSON.stringify(level)
                      : null;
                const messageStr =
                  typeof message === "string"
                    ? message
                    : message != null
                      ? JSON.stringify(message)
                      : null;

                // Use event name as level if it's a known level (info, warning, error, critical, debug)
                // Otherwise use the level attribute
                const effectiveLevel = KNOWN_LEVELS.has(name.toLowerCase())
                  ? name
                  : attrLevelStr;
                const levelStyles = effectiveLevel
                  ? getLevelStyles(effectiveLevel)
                  : null;

                // Don't show name separately if it's a known level (it will be shown in the badge)
                const showName =
                  !KNOWN_LEVELS.has(name.toLowerCase()) && name !== "event";

                return (
                  <div key={idx} className="rounded-md border p-3">
                    <div className="mb-1 flex items-center gap-2">
                      {showName && (
                        <span className="text-sm font-medium">{name}</span>
                      )}
                      {effectiveLevel && levelStyles && (
                        <span
                          className={`flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium ${levelStyles.badgeClass}`}
                        >
                          {levelStyles.icon}
                          {effectiveLevel}
                        </span>
                      )}
                    </div>
                    {messageStr && (
                      <p className="text-sm text-muted-foreground">
                        {messageStr}
                      </p>
                    )}
                    {attrs &&
                      Object.keys(attrs).filter(
                        (k) => k !== "level" && k !== "message",
                      ).length > 0 && (
                        <div className="mt-2">
                          <JsonView
                            value={Object.fromEntries(
                              Object.entries(attrs).filter(
                                ([k]) => k !== "level" && k !== "message",
                              ),
                            )}
                          />
                        </div>
                      )}
                  </div>
                );
              })}
            </div>
          </Section>
        )}

        {/* Attributes - last, fits content */}
        {attributes && !Array.isArray(attributes) && (
          <Section title="Attributes">
            <div className="rounded-md border p-3">
              <JsonView value={attributes} />
            </div>
          </Section>
        )}
      </div>
    </div>
  );
}
