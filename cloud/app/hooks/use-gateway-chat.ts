import type { ChatStatus, UIMessage } from "ai";

import { nanoid } from "nanoid";
import { useCallback, useEffect, useRef, useState } from "react";

import { GatewayClient } from "@/app/lib/gateway-client";

/**
 * Hook that connects to the OpenClaw gateway via WebSocket proxy and provides
 * the same interface as `useMockChat`: `{ messages, status, sendMessage }`.
 *
 * On mount, creates a GatewayClient, connects to the proxy, and loads history.
 * `sendMessage` sends a chat.send RPC and listens for streaming events.
 *
 * Event → UIMessage part mapping:
 * - chat.text.delta     → accumulate into `text` part
 * - chat.reasoning.delta → accumulate into `reasoning` part
 * - chat.tool.start     → create `dynamic-tool` part (state: partial-call)
 * - chat.tool.delta     → update tool part (accumulate input)
 * - chat.tool.output    → update tool part (state: output-available)
 * - chat.tool.error     → update tool part (state: output-error)
 * - chat.done           → set status to ready
 * - chat.error          → set status to error
 */
export function useGatewayChat(orgSlug: string, clawSlug: string) {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("ready");
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const clientRef = useRef<GatewayClient | null>(null);
  const unsubscribesRef = useRef<Array<() => void>>([]);

  // Track parts being built for the current streaming assistant message
  const currentAssistantIdRef = useRef<string | null>(null);
  const currentPartsRef = useRef<UIMessage["parts"][number][]>([]);
  // Map of tool call IDs to their index in currentPartsRef
  const toolPartIndexRef = useRef<Map<string, number>>(new Map());

  const sessionKey = "main:web:default";

  // Helper: update or add the current assistant message
  const updateAssistantMessage = useCallback(
    (assistantId: string, parts: UIMessage["parts"][number][]) => {
      setMessages((prev) => {
        const exists = prev.some((m) => m.id === assistantId);
        if (exists) {
          return prev.map((m) =>
            m.id === assistantId ? { ...m, parts: [...parts] } : m,
          );
        }
        return [
          ...prev,
          { id: assistantId, role: "assistant" as const, parts: [...parts] },
        ];
      });
    },
    [],
  );

  useEffect(() => {
    let mounted = true;
    let client: GatewayClient | null = null;

    // Small delay to survive React strict mode's unmount-remount cycle.
    // The first mount's timer gets cleared on unmount; only the second fires.
    const timer = setTimeout(() => {
      if (!mounted) return;

      client = new GatewayClient();
      clientRef.current = client;

      const connect = async () => {
        try {
          await client!.connect(orgSlug, clawSlug);
          if (!mounted) return;
          setConnectionError(null);

          // Load history
          try {
            const historyRes = await client!.chatHistory({ sessionKey });
            if (!mounted) return;

            // Gateway returns { sessionKey, sessionId, messages: [...] }
            const historyData = historyRes as
              | { messages?: unknown[] }
              | unknown[];
            const rawMessages = Array.isArray(historyData)
              ? historyData
              : ((historyData as { messages?: unknown[] })?.messages ?? []);

            if (Array.isArray(rawMessages) && rawMessages.length > 0) {
              const uiMessages = rawMessages
                .map(historyToUIMessage)
                .filter(Boolean) as UIMessage[];
              setMessages(uiMessages);
            }
          } catch {
            // History load failure is non-fatal
            console.warn("[useGatewayChat] Failed to load history");
          }
        } catch (err) {
          if (!mounted) return;
          setConnectionError(
            err instanceof Error ? err.message : "Connection failed",
          );
          setStatus("error");
        }
      };

      connect();
    }, 100);

    return () => {
      mounted = false;
      clearTimeout(timer);
      for (const unsub of unsubscribesRef.current) {
        unsub();
      }
      unsubscribesRef.current = [];
      if (client) {
        client.disconnect();
      }
      clientRef.current = null;
    };
  }, [orgSlug, clawSlug]);

  const sendMessage = useCallback(
    async (text: string) => {
      const client = clientRef.current;
      if (!client || client.state !== "connected" || status !== "ready") return;

      // Add user message
      const userMessage: UIMessage = {
        id: nanoid(),
        role: "user",
        parts: [{ type: "text", text }],
      };
      setMessages((prev) => [...prev, userMessage]);

      // Prepare streaming state
      const assistantId = nanoid();
      currentAssistantIdRef.current = assistantId;
      currentPartsRef.current = [];
      toolPartIndexRef.current.clear();

      setStatus("submitted");

      // Unsubscribe previous event listeners
      for (const unsub of unsubscribesRef.current) {
        unsub();
      }
      unsubscribesRef.current = [];

      // Subscribe to streaming events.
      // The gateway uses two event types:
      // - "agent": with stream field ("lifecycle", "text", "tool", etc.)
      // - "chat": with state field ("final")
      const unsubs: Array<() => void> = [];

      unsubs.push(
        client.on("agent", (payload) => {
          const p = payload as {
            runId: string;
            stream: string;
            data: Record<string, unknown>;
            sessionKey: string;
          };

          switch (p.stream) {
            case "text": {
              const delta = (p.data.delta ?? p.data.text ?? "") as string;
              if (!delta) break;
              const parts = currentPartsRef.current;
              const lastPart = parts[parts.length - 1];

              if (lastPart && lastPart.type === "text") {
                (lastPart as { type: "text"; text: string }).text += delta;
              } else {
                parts.push({ type: "text", text: delta });
              }

              setStatus("streaming");
              updateAssistantMessage(assistantId, parts);
              break;
            }

            case "reasoning": {
              const delta = (p.data.delta ?? p.data.text ?? "") as string;
              if (!delta) break;
              const parts = currentPartsRef.current;
              const lastPart = parts[parts.length - 1];

              if (lastPart && lastPart.type === "reasoning") {
                (lastPart as { type: "reasoning"; text: string }).text += delta;
              } else {
                parts.push({ type: "reasoning", text: delta });
              }

              setStatus("streaming");
              updateAssistantMessage(assistantId, parts);
              break;
            }

            case "tool": {
              const toolCallId = p.data.toolCallId as string | undefined;
              if (!toolCallId) break;
              const parts = currentPartsRef.current;

              if (p.data.phase === "start" || p.data.state === "start") {
                const toolPart = {
                  type: "dynamic-tool",
                  toolName: p.data.toolName ?? p.data.name ?? "tool",
                  toolCallId,
                  title: (p.data.title ??
                    p.data.toolName ??
                    p.data.name ??
                    "Tool") as string,
                  state: "partial-call",
                  input: {},
                } as unknown as UIMessage["parts"][number];

                toolPartIndexRef.current.set(toolCallId, parts.length);
                parts.push(toolPart);
                setStatus("streaming");
                updateAssistantMessage(assistantId, parts);
              } else if (
                p.data.phase === "output" ||
                p.data.output !== undefined
              ) {
                const idx = toolPartIndexRef.current.get(toolCallId);
                if (idx !== undefined && parts[idx]) {
                  const part = parts[idx] as Record<string, unknown>;
                  part.state = "output-available";
                  part.output = p.data.output;
                }
                updateAssistantMessage(assistantId, parts);
              } else if (
                p.data.phase === "error" ||
                p.data.error !== undefined
              ) {
                const idx = toolPartIndexRef.current.get(toolCallId);
                if (idx !== undefined && parts[idx]) {
                  const part = parts[idx] as Record<string, unknown>;
                  part.state = "output-error";
                  part.errorText = p.data.error;
                }
                updateAssistantMessage(assistantId, parts);
              }
              break;
            }

            case "lifecycle": {
              if (p.data.phase === "start") {
                setStatus("streaming");
              } else if (p.data.phase === "error") {
                const errMsg = (p.data.message ??
                  p.data.error ??
                  "Agent error") as string;
                const parts = currentPartsRef.current;
                parts.push({ type: "text", text: `Error: ${errMsg}` });
                updateAssistantMessage(assistantId, parts);
                setStatus("ready");
                currentAssistantIdRef.current = null;
              }
              break;
            }
          }
        }),
      );

      unsubs.push(
        client.on("chat", (payload) => {
          const p = payload as { state?: string; runId?: string };
          if (p.state === "final") {
            setStatus("ready");
            currentAssistantIdRef.current = null;
          }
        }),
      );

      // Log all events for debugging
      unsubs.push(
        client.on("*", (payload) => {
          const p = payload as { event: string; payload: unknown };
          console.log("[useGatewayChat] Event:", p.event, p.payload);
        }),
      );

      unsubscribesRef.current = unsubs;

      // Send the chat message
      try {
        await client.chatSend({
          sessionKey,
          message: text,
          idempotencyKey: nanoid(),
        });
        // The response to chat.send just confirms the run started.
        // Actual content comes via events above.
        setStatus("streaming");
      } catch (err) {
        console.error("[useGatewayChat] chat.send failed:", err);
        setStatus("ready");
      }
    },
    [status, updateAssistantMessage],
  );

  return { messages, status, sendMessage, connectionError };
}

// ---------------------------------------------------------------------------
// History conversion
// ---------------------------------------------------------------------------

/**
 * Convert a gateway history entry into a UIMessage.
 * The exact shape depends on the gateway's history format — this is a
 * best-effort mapping that will be refined against a live gateway.
 */
function historyToUIMessage(entry: unknown): UIMessage | null {
  if (typeof entry !== "object" || entry === null) return null;
  const e = entry as Record<string, unknown>;

  const role = e.role as string | undefined;
  if (role !== "user" && role !== "assistant") return null;

  const parts: UIMessage["parts"][number][] = [];

  // Gateway format: content is an array of {type: "text", text: "..."} objects
  if (Array.isArray(e.content)) {
    for (const item of e.content) {
      if (typeof item === "object" && item !== null) {
        const c = item as Record<string, unknown>;
        if (c.type === "text" && typeof c.text === "string" && c.text) {
          parts.push({ type: "text", text: c.text });
        }
      }
    }
  } else if (typeof e.content === "string" && e.content) {
    parts.push({ type: "text", text: e.content });
  }

  if (parts.length === 0) return null;

  return {
    id: (e.id as string) ?? nanoid(),
    role: role as "user" | "assistant",
    parts,
  };
}
