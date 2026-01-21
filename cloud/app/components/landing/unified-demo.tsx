import { useState } from "react";
import { ChevronDown, Wrench } from "lucide-react";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import MirascopeLogo from "@/app/components/blocks/branding/mirascope-logo";
import { cn } from "@/app/lib/utils";
import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/app/components/ai-elements/message";
import {
  Reasoning,
  ReasoningTrigger,
  ReasoningContent,
} from "@/app/components/ai-elements/reasoning";

// Types
type ProviderId = "openai" | "anthropic" | "google";

interface Trace {
  id: string;
  version: number;
  timestamp: string;
  inputTokens: number;
  outputTokens: number;
  cost: number;
  input: string;
  output: string;
  thinking?: string;
  toolCall?: {
    name: string;
    input: Record<string, unknown>;
    output: unknown;
  };
}

interface ProviderConfig {
  id: ProviderId;
  label: string;
  model: string;
  overrideModel: string;
}

const PROVIDERS: ProviderConfig[] = [
  {
    id: "openai",
    label: "OpenAI",
    model: "openai/gpt-5.2",
    overrideModel: "anthropic/claude-opus-4-5",
  },
  {
    id: "anthropic",
    label: "Anthropic",
    model: "anthropic/claude-opus-4-5",
    overrideModel: "google/gemini-3-pro-preview",
  },
  {
    id: "google",
    label: "Google",
    model: "google/gemini-3-pro-preview",
    overrideModel: "openai/gpt-5.2",
  },
];

// Sample trace data
const TRACES: Trace[] = [
  {
    id: "trace_1",
    version: 2,
    timestamp: "1 min ago",
    input: "Recommend some **sci-fi** books",
    output:
      "Based on our library, I'd recommend these sci-fi classics:\n\n- **Dune** by Frank Herbert - An epic tale of politics and survival\n- **Foundation** by Isaac Asimov - A groundbreaking series about civilization",
    inputTokens: 156,
    outputTokens: 89,
    cost: 0.0024,
    thinking:
      "The user wants sci-fi recommendations. Let me search the library.",
    toolCall: {
      name: "library",
      input: { genre: "sci-fi" },
      output: ["Dune", "Foundation"],
    },
  },
  {
    id: "trace_2",
    version: 2,
    timestamp: "2 mins ago",
    input: "What **fantasy** books do you have?",
    output:
      "Here's what we have in fantasy:\n\n- **The Name of the Wind** by Patrick Rothfuss - Beautiful prose and magic\n- **The Way of Kings** by Brandon Sanderson - Epic worldbuilding",
    inputTokens: 142,
    outputTokens: 67,
    cost: 0.0019,
    thinking: "Looking for fantasy books. Let me check the library.",
    toolCall: {
      name: "library",
      input: { genre: "fantasy" },
      output: ["The Name of the Wind", "The Way of Kings"],
    },
  },
  {
    id: "trace_3",
    version: 1,
    timestamp: "1 hr ago",
    input: "Find me **mystery** novels",
    output:
      "I couldn't find any mystery novels in our collection. Would you like me to recommend something from **sci-fi** or **fantasy** instead?",
    inputTokens: 138,
    outputTokens: 52,
    cost: 0.0016,
    thinking: "Looking for mystery novels. Let me check the library.",
    toolCall: {
      name: "library",
      input: { genre: "mystery" },
      output: [],
    },
  },
];

function getCodeExample(provider: ProviderConfig, query: string): string {
  // Strip markdown bold syntax from the query for the code example
  const cleanQuery = query.replace(/\*\*/g, "");
  return `from mirascope import llm, ops

@llm.tool
def library(genre: str) -> list[str]:
    """Search library for books by genre."""
    books = {
        "sci-fi": ["Dune", "Foundation"],
        "fantasy": ["The Name of the Wind", "The Way of Kings"],
    }
    return books.get(genre, [])

@ops.version()  # Automatic versioning, tracing, and cost tracking
@llm.call(
    "${provider.model}",
    tools=[library],
    thinking={"include_thoughts": True},
)
def librarian(query: str) -> str:
    return query

# Agent Loop
response = librarian("${cleanQuery}")
while response.tool_calls:
    tool_outputs = response.execute_tools()
    response = response.resume(tool_outputs)

print(response.text())`;
}

interface TraceRowProps {
  trace: Trace;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

function TraceRow({ trace, isSelected, onSelect }: TraceRowProps) {
  return (
    <div
      className={cn(
        "flex w-full cursor-pointer text-sm transition-colors",
        isSelected
          ? "bg-mirple/20 dark:bg-mirple/30"
          : "hover:bg-slate-100 dark:hover:bg-muted",
      )}
      onClick={() => onSelect(trace.id)}
    >
      <div className="border-slate-100 dark:border-border/50 text-slate-800 dark:text-foreground w-[15%] flex-shrink-0 border-t px-1.5 py-1.5 text-center">
        {trace.version}
      </div>
      <div className="border-slate-100 dark:border-border/50 text-slate-600 dark:text-muted-foreground w-[27%] flex-shrink-0 border-t px-1.5 py-1.5">
        {trace.timestamp}
      </div>
      <div className="border-slate-100 dark:border-border/50 text-slate-600 dark:text-muted-foreground w-[17%] flex-shrink-0 border-t px-1.5 py-1.5 text-right">
        {trace.inputTokens}
      </div>
      <div className="border-slate-100 dark:border-border/50 text-slate-600 dark:text-muted-foreground w-[17%] flex-shrink-0 border-t px-1.5 py-1.5 text-right">
        {trace.outputTokens}
      </div>
      <div className="border-slate-100 dark:border-border/50 text-slate-600 dark:text-muted-foreground w-[24%] flex-shrink-0 border-t px-1.5 py-1.5 text-right">
        ${trace.cost.toFixed(4)}
      </div>
    </div>
  );
}

interface CompactToolCallProps {
  toolCall: NonNullable<Trace["toolCall"]>;
}

function CompactToolCall({ toolCall }: CompactToolCallProps) {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="max-w-[280px] rounded-md border border-slate-200 bg-slate-50 text-xs dark:border-border dark:bg-muted/50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center gap-2 px-2.5 py-1.5 text-left"
      >
        <Wrench className="size-3.5 text-slate-500" />
        <span className="font-medium text-slate-800 dark:text-foreground">
          {toolCall.name}
        </span>
        <ChevronDown
          className={cn(
            "ml-auto size-3.5 text-slate-400 transition-transform",
            isOpen && "rotate-180",
          )}
        />
      </button>
      {isOpen && (
        <div className="border-t border-slate-200 px-2.5 py-2 font-mono text-[11px] dark:border-border">
          <div className="mb-1">
            <span className="text-slate-400">in: </span>
            <span className="text-slate-600 dark:text-muted-foreground">
              {JSON.stringify(toolCall.input)}
            </span>
          </div>
          <div>
            <span className="text-slate-400">out: </span>
            <span className="text-slate-700 dark:text-foreground">
              {JSON.stringify(toolCall.output)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

interface MessagesSectionProps {
  trace: Trace;
}

function MessagesSection({ trace }: MessagesSectionProps) {
  const [reasoningOpen, setReasoningOpen] = useState(true);

  return (
    <div className="flex flex-col gap-3 p-4 text-slate-800 dark:text-foreground">
      {/* User Message */}
      <Message from="user">
        <MessageContent className="text-xs">
          <MessageResponse className="text-xs [&_p]:my-0 [&_strong]:font-bold">
            {trace.input}
          </MessageResponse>
        </MessageContent>
      </Message>

      {/* Thinking (if available) */}
      {trace.thinking && (
        <Reasoning
          open={reasoningOpen}
          onOpenChange={setReasoningOpen}
          duration={2}
        >
          <ReasoningTrigger className="text-xs text-slate-500 hover:text-slate-700 dark:text-muted-foreground dark:hover:text-foreground" />
          <ReasoningContent className="text-xs text-slate-600 dark:text-foreground">
            {trace.thinking}
          </ReasoningContent>
        </Reasoning>
      )}

      {/* Tool Call (if available) */}
      {trace.toolCall && <CompactToolCall toolCall={trace.toolCall} />}

      {/* Assistant Message */}
      <Message from="assistant">
        <MessageContent className="text-xs text-slate-800 dark:text-foreground">
          <MessageResponse className="text-xs text-slate-800 dark:text-foreground [&_p]:my-0.5 [&_p]:leading-snug [&_li]:my-0 [&_strong]:text-slate-900 dark:[&_strong]:text-white">
            {trace.output}
          </MessageResponse>
        </MessageContent>
      </Message>
    </div>
  );
}

interface ProviderTabsProps {
  providers: ProviderConfig[];
  selectedProvider: ProviderId;
  onSelect: (id: ProviderId) => void;
}

function ProviderTabs({
  providers,
  selectedProvider,
  onSelect,
}: ProviderTabsProps) {
  return (
    <div className="flex gap-1">
      {providers.map((provider) => (
        <button
          key={provider.id}
          onClick={() => onSelect(provider.id)}
          className={cn(
            "rounded px-2.5 py-1 text-xs font-medium transition-colors",
            selectedProvider === provider.id
              ? "bg-mirple text-white"
              : "text-slate-600 dark:text-muted-foreground hover:bg-mirple/20 hover:text-slate-900 dark:hover:text-foreground",
          )}
        >
          {provider.label}
        </button>
      ))}
    </div>
  );
}

interface UnifiedDemoProps {
  className?: string;
}

export function UnifiedDemo({ className }: UnifiedDemoProps) {
  const [selectedTraceId, setSelectedTraceId] = useState<string>(TRACES[0].id);
  const [selectedProviderId, setSelectedProviderId] =
    useState<ProviderId>("openai");
  const selectedTrace =
    TRACES.find((trace) => trace.id === selectedTraceId) || TRACES[0];
  const selectedProvider =
    PROVIDERS.find((p) => p.id === selectedProviderId) || PROVIDERS[0];

  return (
    <div
      className={cn(
        "border-slate-200 dark:border-border bg-white dark:bg-background w-full overflow-hidden rounded-lg border shadow-lg",
        className,
      )}
    >
      {/* Header with Provider Tabs */}
      <div className="border-slate-200 dark:border-border bg-slate-100 dark:bg-primary/10 flex items-center justify-between border-b px-3 py-1.5">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-900 dark:text-foreground">
            librarian
          </span>
          <ProviderTabs
            providers={PROVIDERS}
            selectedProvider={selectedProviderId}
            onSelect={setSelectedProviderId}
          />
        </div>
        <div className="flex flex-row items-center gap-1">
          <MirascopeLogo size="micro" withText={true} />
          <span className="text-mirple text-xs font-medium">Cloud</span>
        </div>
      </div>

      {/* Main Content: Code on left, Traces/Messages on right */}
      <div className="flex flex-col md:flex-row">
        {/* Code Section - Left */}
        <div className="border-slate-200 dark:border-border md:w-[55%] md:border-r">
          <CodeBlock
            code={getCodeExample(selectedProvider, selectedTrace.input)}
            language="python"
            className="rounded-none border-none"
            showLineNumbers={false}
          />
        </div>

        {/* Right Panel: Traces on top, Messages on bottom */}
        <div className="bg-slate-50 dark:bg-primary/5 flex flex-col md:w-[45%]">
          {/* Traces Table */}
          <div className="border-slate-200 dark:border-border border-b">
            <div className="border-slate-200 dark:border-border bg-slate-100 dark:bg-primary/10 border-b px-3 py-1.5">
              <h3 className="text-xs font-semibold text-slate-900 dark:text-foreground">
                Traces
              </h3>
            </div>
            <div>
              {/* Table Header */}
              <div className="bg-slate-50 dark:bg-primary/5 sticky top-0 flex w-full text-xs">
                <div className="text-slate-500 dark:text-muted-foreground w-[15%] flex-shrink-0 px-1.5 py-1 text-center font-medium">
                  Version
                </div>
                <div className="text-slate-500 dark:text-muted-foreground w-[27%] flex-shrink-0 px-1.5 py-1 font-medium">
                  Time
                </div>
                <div className="text-slate-500 dark:text-muted-foreground w-[17%] flex-shrink-0 px-1.5 py-1 text-right font-medium">
                  In
                </div>
                <div className="text-slate-500 dark:text-muted-foreground w-[17%] flex-shrink-0 px-1.5 py-1 text-right font-medium">
                  Out
                </div>
                <div className="text-slate-500 dark:text-muted-foreground w-[24%] flex-shrink-0 px-1.5 py-1 text-right font-medium">
                  Cost
                </div>
              </div>
              {/* Table Rows */}
              {TRACES.map((trace) => (
                <TraceRow
                  key={trace.id}
                  trace={trace}
                  isSelected={selectedTraceId === trace.id}
                  onSelect={setSelectedTraceId}
                />
              ))}
            </div>
          </div>

          {/* Messages Pane */}
          <div className="flex flex-1 flex-col">
            <div className="border-slate-200 dark:border-border bg-slate-100 dark:bg-primary/10 border-b px-3 py-1.5">
              <h3 className="text-xs font-semibold text-slate-900 dark:text-foreground">
                Messages
              </h3>
            </div>
            <div className="overflow-y-auto">
              <MessagesSection trace={selectedTrace} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
