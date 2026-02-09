import type { DynamicToolUIPart, SourceUrlUIPart, UIMessage } from "ai";

import { createFileRoute } from "@tanstack/react-router";
import { isToolUIPart } from "ai";

import {
  Conversation,
  ConversationContent,
  ConversationEmptyState,
  ConversationScrollButton,
} from "@/app/components/ai-elements/conversation";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/app/components/ai-elements/message";
import {
  PromptInput,
  PromptInputFooter,
  PromptInputSubmit,
  PromptInputTextarea,
} from "@/app/components/ai-elements/prompt-input";
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from "@/app/components/ai-elements/reasoning";
import {
  Source,
  Sources,
  SourcesContent,
  SourcesTrigger,
} from "@/app/components/ai-elements/sources";
import {
  Tool,
  ToolContent,
  ToolHeader,
  ToolInput,
  ToolOutput,
} from "@/app/components/ai-elements/tool";
import { ClawHeader } from "@/app/components/claw-header";
import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { useClaw } from "@/app/contexts/claw";
import { useMockChat } from "@/app/hooks/use-mock-chat";

function MessageParts({
  message,
  isLastMessage,
  chatStatus,
}: {
  message: UIMessage;
  isLastMessage: boolean;
  chatStatus: string;
}) {
  // Collect source-url parts to render as a group
  const sources = message.parts.filter(
    (p): p is SourceUrlUIPart => p.type === "source-url",
  );

  const lastPartIndex = message.parts.length - 1;

  return (
    <>
      {message.parts.map((part, i) => {
        switch (part.type) {
          case "text":
            return <MessageResponse key={i}>{part.text}</MessageResponse>;

          case "reasoning":
            return (
              <Reasoning
                key={i}
                isStreaming={
                  isLastMessage &&
                  chatStatus === "streaming" &&
                  i === lastPartIndex
                }
                defaultOpen
              >
                <ReasoningTrigger />
                <ReasoningContent>{part.text}</ReasoningContent>
              </Reasoning>
            );

          case "source-url":
            // Render all sources together at the position of the first one
            if (sources[0] !== part) return null;
            return (
              <Sources key={i}>
                <SourcesTrigger count={sources.length} />
                <SourcesContent>
                  {sources.map((s) => (
                    <Source href={s.url} key={s.sourceId} title={s.title} />
                  ))}
                </SourcesContent>
              </Sources>
            );

          default: {
            if (isToolUIPart(part)) {
              const toolPart = part as DynamicToolUIPart;
              return (
                <Tool key={i}>
                  <ToolHeader
                    title={toolPart.title ?? toolPart.toolName}
                    type={`tool-${toolPart.toolName}` as const}
                    state={toolPart.state}
                  />
                  <ToolContent>
                    {"input" in toolPart && toolPart.input != null && (
                      <ToolInput input={toolPart.input} />
                    )}
                    {("output" in toolPart || "errorText" in toolPart) && (
                      <ToolOutput
                        output={
                          "output" in toolPart ? toolPart.output : undefined
                        }
                        errorText={
                          "errorText" in toolPart
                            ? toolPart.errorText
                            : undefined
                        }
                      />
                    )}
                  </ToolContent>
                </Tool>
              );
            }
            return null;
          }
        }
      })}
    </>
  );
}

function ClawsChatPage() {
  const { selectedClaw } = useClaw();
  const { messages, status, sendMessage } = useMockChat();

  return (
    <Protected>
      <CloudLayout>
        <div className="flex h-full flex-col overflow-hidden">
          <div className="shrink-0 p-6 pb-0">
            <ClawHeader />
          </div>
          <div className="relative min-h-0 flex-1">
            <Conversation className="absolute inset-0">
              <ConversationContent>
                {messages.length === 0 ? (
                  <ConversationEmptyState />
                ) : (
                  messages.map((msg, msgIndex) => (
                    <Message from={msg.role} key={msg.id}>
                      <MessageContent>
                        <MessageParts
                          chatStatus={status}
                          isLastMessage={msgIndex === messages.length - 1}
                          message={msg}
                        />
                      </MessageContent>
                    </Message>
                  ))
                )}
              </ConversationContent>
              <ConversationScrollButton />
            </Conversation>
          </div>
          <div className="shrink-0 px-6 pb-6">
            <PromptInput
              onSubmit={(message) => {
                if (message.text.trim()) {
                  sendMessage(message.text);
                }
              }}
            >
              <PromptInputTextarea
                className="min-h-0 pr-14 font-sans"
                disabled={!selectedClaw}
                placeholder={
                  selectedClaw
                    ? "What would you like to know?"
                    : "Select a claw to start chatting"
                }
              />
              <PromptInputFooter className="absolute right-1.5 bottom-1.5 w-auto px-0 pb-0">
                <PromptInputSubmit
                  disabled={!selectedClaw || status !== "ready"}
                  status={status}
                />
              </PromptInputFooter>
            </PromptInput>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/claws/chat")({
  component: ClawsChatPage,
});
