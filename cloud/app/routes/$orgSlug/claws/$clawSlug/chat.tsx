import type { DynamicToolUIPart, SourceUrlUIPart, UIMessage } from "ai";

import { createFileRoute } from "@tanstack/react-router";
import { isToolUIPart } from "ai";
import { ExternalLink } from "lucide-react";

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
import { Button } from "@/app/components/ui/button";
import { useClaw } from "@/app/contexts/claw";
import { useGatewayChat } from "@/app/hooks/use-gateway-chat";

function getGatewayUrl(orgSlug: string, clawSlug: string): string {
  if (typeof window === "undefined") return "#";
  const hostname = window.location.hostname;
  if (hostname === "localhost" || hostname === "127.0.0.1") {
    // In local dev, link directly to the local OpenClaw Control UI.
    // Derive HTTP URL from the WS proxy URL (ws://host:port → http://host:port).
    const wsUrl = import.meta.env.VITE_OPENCLAW_GATEWAY_WS_URL;
    if (wsUrl) {
      return wsUrl.replace(/^wss:/, "https:").replace(/^ws:/, "http:");
    }
    return "http://localhost:18789/";
  }
  // Derive dispatch worker URL from current hostname:
  // staging.mirascope.com → openclaw.staging.mirascope.com
  // dev.mirascope.com     → openclaw.dev.mirascope.com
  // mirascope.com         → openclaw.mirascope.com
  const match = hostname.match(/^([\w-]+)\.(mirascope\.com)$/);
  const base =
    match && match[1] !== "www"
      ? `openclaw.${match[1]}.${match[2]}`
      : "openclaw.mirascope.com";
  return `https://${base}/${orgSlug}/${clawSlug}/overview`;
}

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
  const { orgSlug, clawSlug } = Route.useParams();
  const { messages, status, sendMessage, connectionError } = useGatewayChat(
    orgSlug,
    clawSlug,
  );

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex shrink-0 items-center justify-end px-6">
        <Button asChild size="sm" variant="outline">
          <a
            href={getGatewayUrl(orgSlug, clawSlug)}
            rel="noopener noreferrer"
            target="_blank"
          >
            <ExternalLink className="mr-1.5 size-4" />
            OpenClaw Gateway
          </a>
        </Button>
      </div>
      <div className="relative min-h-0 flex-1">
        {connectionError && (
          <div className="bg-destructive/10 text-destructive mx-6 mt-2 rounded-md px-4 py-2 text-sm">
            Connection error: {connectionError}
          </div>
        )}
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
            disabled={!selectedClaw || !!connectionError}
            placeholder={
              connectionError
                ? "Unable to connect to gateway"
                : selectedClaw
                  ? "What's up?"
                  : "Select a claw to start chatting"
            }
          />
          <PromptInputFooter className="absolute right-1.5 bottom-1.5 w-auto px-0 pb-0">
            <PromptInputSubmit
              disabled={
                !selectedClaw || !!connectionError || status !== "ready"
              }
              status={status}
            />
          </PromptInputFooter>
        </PromptInput>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/$orgSlug/claws/$clawSlug/chat")({
  component: ClawsChatPage,
});
