import type { ChatStatus, UIMessage } from "ai";

import { nanoid } from "nanoid";
import { useCallback, useEffect, useRef, useState } from "react";

/**
 * A canned response is an array of "stages". Each stage has a set of parts
 * and a delay (ms) before advancing to the next stage. Text parts within a
 * stage are streamed character-by-character; all other part types appear
 * instantly when their stage begins.
 */
type ResponseStage = {
  parts: UIMessage["parts"][number][];
  /** ms to wait before starting the next stage (default 300) */
  delay?: number;
};

const CANNED_RESPONSES: ResponseStage[][] = [
  // ── Response 1: Reasoning → text ──────────────────────────────────────
  [
    {
      parts: [
        {
          type: "reasoning",
          text: "The user is asking about setting up Mirascope. I should walk them through the key steps: installation, environment configuration, and running a first call. Let me keep it concise but cover the essentials.",
        },
      ],
      delay: 400,
    },
    {
      parts: [
        {
          type: "text",
          text: `Sure, I can help with that! Here's a quick overview:

- First, make sure your environment is set up correctly
- Then, configure the required parameters
- Finally, run the deployment script

Let me know if you need more details on any of these steps.`,
        },
      ],
    },
  ],

  // ── Response 2: Reasoning → tool call → text with code ────────────────
  [
    {
      parts: [
        {
          type: "reasoning",
          text: "They want a code example. Let me search the docs for a good @llm.call sample, then write a clean Python snippet showing the decorator pattern.",
        },
      ],
      delay: 400,
    },
    {
      parts: [
        {
          type: "dynamic-tool",
          toolName: "search_docs",
          toolCallId: nanoid(),
          title: "Search documentation",
          state: "output-available",
          input: { query: "llm.call decorator example" },
          output: {
            results: [
              "mirascope.llm.call — Decorator for LLM API calls",
              "Quick Start — Your first Mirascope call",
            ],
          },
        } as UIMessage["parts"][number],
      ],
      delay: 300,
    },
    {
      parts: [
        {
          type: "text",
          text: `Here's an example using Python:

\`\`\`python
from mirascope.llm import llm

@llm.call(model="anthropic:claude-sonnet-4-20250514")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

response = recommend_book("fantasy")
print(response.content)
\`\`\`

This will call the model and return a structured response.`,
        },
      ],
    },
  ],

  // ── Response 3: Tool call (running) → tool call (error) → text ────────
  [
    {
      parts: [
        {
          type: "dynamic-tool",
          toolName: "run_tests",
          toolCallId: nanoid(),
          title: "Run test suite",
          state: "output-available",
          input: { suite: "unit", path: "tests/" },
          output: { passed: 47, failed: 0, skipped: 2 },
        } as UIMessage["parts"][number],
        {
          type: "dynamic-tool",
          toolName: "check_types",
          toolCallId: nanoid(),
          title: "Type check",
          state: "output-error",
          input: { strict: true },
          errorText:
            "Type error in module 'auth': Argument of type 'string' is not assignable to parameter of type 'number'.",
        } as UIMessage["parts"][number],
      ],
      delay: 300,
    },
    {
      parts: [
        {
          type: "text",
          text: `Great question! There are a few things to consider:

1. **Performance** — Keep your prompts concise to reduce latency
2. **Cost** — Use streaming for long responses to improve perceived speed
3. **Reliability** — Always handle API errors gracefully

> Pro tip: You can use \`@llm.call\` with retries built in for production workloads.`,
        },
      ],
    },
  ],

  // ── Response 4: Reasoning → tool → sources → text ────────────────────
  [
    {
      parts: [
        {
          type: "reasoning",
          text: "This looks like a configuration issue. Let me look up the relevant settings and find documentation links to share.",
        },
      ],
      delay: 300,
    },
    {
      parts: [
        {
          type: "dynamic-tool",
          toolName: "read_config",
          toolCallId: nanoid(),
          title: "Read configuration",
          state: "output-available",
          input: { file: "settings.yaml" },
          output: { timeout: 5, retries: 1, backoff_factor: 1 },
        } as UIMessage["parts"][number],
      ],
      delay: 300,
    },
    {
      parts: [
        {
          type: "source-url",
          sourceId: nanoid(),
          url: "https://docs.mirascope.io/configuration",
          title: "Configuration Reference",
        },
        {
          type: "source-url",
          sourceId: nanoid(),
          url: "https://docs.mirascope.io/troubleshooting/timeouts",
          title: "Troubleshooting Timeouts",
        },
        {
          type: "text",
          text: `I've analyzed the issue and here's what I found:

The problem is in the configuration file. You need to update the \`timeout\` setting:

\`\`\`yaml
settings:
  timeout: 30
  retries: 3
  backoff_factor: 2
\`\`\`

After making this change, restart the service and it should resolve the timeout errors you're seeing.`,
        },
      ],
    },
  ],
];

export function useMockChat() {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [status, setStatus] = useState<ChatStatus>("ready");
  const responseIndexRef = useRef(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const sendMessage = useCallback(
    (text: string) => {
      if (status !== "ready") return;

      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      const userMessage: UIMessage = {
        id: nanoid(),
        role: "user",
        parts: [{ type: "text", text }],
      };

      const assistantId = nanoid();
      const stages =
        CANNED_RESPONSES[responseIndexRef.current % CANNED_RESPONSES.length];
      responseIndexRef.current++;

      setMessages((prev) => [...prev, userMessage]);
      setStatus("submitted");

      // Accumulated parts from all completed stages
      let completedParts: UIMessage["parts"][number][] = [];

      const runStage = (stageIndex: number) => {
        if (stageIndex >= stages.length) {
          setStatus("ready");
          return;
        }

        const stage = stages[stageIndex];
        const delay = stage.delay ?? 300;

        // Find the text part to stream (if any) in this stage
        const textPartIndex = stage.parts.findIndex((p) => p.type === "text");
        const textPart =
          textPartIndex !== -1
            ? (stage.parts[textPartIndex] as { type: "text"; text: string })
            : null;
        const nonTextParts = stage.parts.filter((p) => p.type !== "text");

        if (stageIndex === 0) {
          setStatus("streaming");
        }

        // Show non-text parts immediately (reasoning, tools, sources)
        // For reasoning parts, show them as streaming first
        const reasoningPart = nonTextParts.find(
          (p) => p.type === "reasoning",
        ) as { type: "reasoning"; text: string } | undefined;
        const otherParts = nonTextParts.filter((p) => p.type !== "reasoning");

        if (reasoningPart) {
          // Stream reasoning text character by character
          const fullReasoning = reasoningPart.text;
          let reasoningCharIndex = 0;

          // Show empty reasoning part first
          const currentParts = [
            ...completedParts,
            ...otherParts,
            { type: "reasoning" as const, text: "" },
          ];
          setMessages((prev) =>
            updateOrAddAssistant(prev, assistantId, currentParts),
          );

          intervalRef.current = setInterval(() => {
            reasoningCharIndex++;
            const currentText = fullReasoning.slice(0, reasoningCharIndex);
            const updatedParts = [
              ...completedParts,
              ...otherParts,
              { type: "reasoning" as const, text: currentText },
            ];
            setMessages((prev) =>
              updateOrAddAssistant(prev, assistantId, updatedParts),
            );

            if (reasoningCharIndex >= fullReasoning.length) {
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
              }
              completedParts = [
                ...completedParts,
                ...otherParts,
                { type: "reasoning" as const, text: fullReasoning },
              ];

              if (textPart) {
                streamTextPart(
                  assistantId,
                  textPart.text,
                  completedParts,
                  stageIndex,
                  stages.length,
                  delay,
                  runStage,
                );
              } else {
                timeoutRef.current = setTimeout(
                  () => runStage(stageIndex + 1),
                  delay,
                );
              }
            }
          }, 10);
        } else if (nonTextParts.length > 0 && !textPart) {
          // Only non-text, non-reasoning parts (tools, sources, etc.)
          completedParts = [...completedParts, ...nonTextParts];
          setMessages((prev) =>
            updateOrAddAssistant(prev, assistantId, completedParts),
          );
          timeoutRef.current = setTimeout(
            () => runStage(stageIndex + 1),
            delay,
          );
        } else if (textPart && nonTextParts.length > 0) {
          // Non-text parts + text to stream
          completedParts = [...completedParts, ...nonTextParts];
          setMessages((prev) =>
            updateOrAddAssistant(prev, assistantId, completedParts),
          );
          streamTextPart(
            assistantId,
            textPart.text,
            completedParts,
            stageIndex,
            stages.length,
            delay,
            runStage,
          );
        } else if (textPart) {
          // Only text to stream
          streamTextPart(
            assistantId,
            textPart.text,
            completedParts,
            stageIndex,
            stages.length,
            delay,
            runStage,
          );
        } else {
          // Empty stage
          timeoutRef.current = setTimeout(
            () => runStage(stageIndex + 1),
            delay,
          );
        }
      };

      const streamTextPart = (
        asstId: string,
        fullText: string,
        baseParts: UIMessage["parts"][number][],
        stageIndex: number,
        totalStages: number,
        delay: number,
        next: (i: number) => void,
      ) => {
        let charIndex = 0;
        intervalRef.current = setInterval(() => {
          charIndex++;
          const currentText = fullText.slice(0, charIndex);
          const updatedParts = [
            ...baseParts,
            { type: "text" as const, text: currentText },
          ];
          setMessages((prev) =>
            updateOrAddAssistant(prev, asstId, updatedParts),
          );

          if (charIndex >= fullText.length) {
            if (intervalRef.current) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }
            completedParts = [
              ...baseParts,
              { type: "text" as const, text: fullText },
            ];

            if (stageIndex < totalStages - 1) {
              timeoutRef.current = setTimeout(
                () => next(stageIndex + 1),
                delay,
              );
            } else {
              setStatus("ready");
            }
          }
        }, 15);
      };

      // Kick off after the initial "submitted" delay
      timeoutRef.current = setTimeout(() => runStage(0), 300);
    },
    [status],
  );

  return { messages, status, sendMessage };
}

function updateOrAddAssistant(
  messages: UIMessage[],
  assistantId: string,
  parts: UIMessage["parts"][number][],
): UIMessage[] {
  const exists = messages.some((m) => m.id === assistantId);
  if (exists) {
    return messages.map((m) => (m.id === assistantId ? { ...m, parts } : m));
  }
  return [...messages, { id: assistantId, role: "assistant" as const, parts }];
}
