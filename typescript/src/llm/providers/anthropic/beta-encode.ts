/** Request encoding for Anthropic structured outputs and strict tools. */

import type { MessageCreateParamsNonStreaming as BetaParams } from "@anthropic-ai/sdk/resources/beta/messages/messages";

import type { Format } from "@/llm/formatting";
import type { Message } from "@/llm/messages";
import type { Params } from "@/llm/models";
import type { AnthropicModelId } from "@/llm/providers/anthropic/model-id";
import type { Tools } from "@/llm/tools";

import { buildRequestParams } from "@/llm/providers/anthropic/_utils";

function strictSchema(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(strictSchema);
  if (typeof value !== "object" || value === null) return value;
  const schema = value as Record<string, unknown>;
  const result: Record<string, unknown> = {};
  for (const [key, child] of Object.entries(schema)) {
    result[key] = strictSchema(child);
  }
  if (schema.type === "object") result.additionalProperties = false;
  return result;
}

export function buildBetaRequestParams(
  modelId: AnthropicModelId,
  messages: readonly Message[],
  tools?: Tools,
  format?: Format | null,
  params?: Params,
): BetaParams {
  const standard = buildRequestParams(
    modelId,
    messages,
    tools,
    format?.mode === "strict" ? null : format,
    params,
    true,
  );
  const beta: BetaParams = {
    ...standard,
    betas: ["structured-outputs-2025-11-13"],
  };

  if (format?.mode === "strict") {
    beta.output_format = {
      type: "json_schema",
      schema: strictSchema(format.schema) as Record<string, unknown>,
    };
  }

  if (beta.tools) {
    beta.tools = beta.tools.map((encoded) => {
      if (!("name" in encoded) || !("input_schema" in encoded)) {
        return encoded;
      }
      const original = tools?.find(
        (tool) => "parameters" in tool && tool.name === encoded.name,
      );
      const schema =
        original && "parameters" in original
          ? original.parameters
          : format?.mode === "tool" &&
              format.createToolSchema().name === encoded.name
            ? format.schema
            : /* v8 ignore next 1 - defensive fallback for an SDK-only tool */
              encoded.input_schema;
      const strict =
        original && "strict" in original ? original.strict !== false : true;
      return {
        ...encoded,
        input_schema: {
          ...(strict
            ? (strictSchema(schema) as Record<string, unknown>)
            : schema),
          type: "object" as const,
        },
        strict,
      };
    });
  }

  return beta;
}
