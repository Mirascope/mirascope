import { useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { useProvider } from "@/src/components/mdx/providers";
import { replaceProviderVariables } from "@/src/config/providers";
import { LilypadLogo } from "@/src/components/core/branding";
import { AnalyticsCodeBlock } from "@/src/components/mdx/elements/AnalyticsCodeBlock";

// Types
interface MessageCardProps {
  type: "user" | "assistant";
  content: string;
}

type TraceLabel = "pass" | "fail";

interface Trace {
  id: string;
  version: number;
  label: TraceLabel;
  timestamp: string;
  promptTemplate: string;
  question: string;
  output: string;
  cost: number;
  tokens: number;
}

interface HeaderProps {
  functionName: string;
  version: number;
}

interface CodePaneProps {
  code: string;
}

interface TraceRowProps {
  trace: Trace;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

interface TracesTableProps {
  traces: Trace[];
  selectedTraceId: string;
  onSelectTrace: (id: string) => void;
}

interface MessagesPaneProps {
  input: string;
  output: string;
}

// Component: MessageCard
function MessageCard({ type, content }: MessageCardProps) {
  const badgeClass =
    type === "user" ? "bg-muted text-muted-foreground" : "bg-primary/10 text-primary";

  return (
    <div className="bg-muted/20 rounded-lg px-3 py-1">
      <div className="flex flex-col">
        <span
          className={`${badgeClass} mb-1.5 self-start rounded px-1.5 py-0.5 text-xs font-medium`}
        >
          {type === "user" ? "user" : "assistant"}
        </span>
        <pre className="font-mono text-xs break-words whitespace-pre-wrap">
          <code>{content}</code>
        </pre>
      </div>
    </div>
  );
}

// Component: Header
function Header({ functionName, version }: HeaderProps) {
  return (
    <div className="border-border/60 bg-muted flex items-center justify-between border-b px-2 py-2">
      <div className="flex items-center gap-2">
        <span className="text-sm font-semibold">{functionName}</span>
        <span className="bg-primary text-primary-foreground rounded-full px-2 py-0.5 text-xs">
          v{version}
        </span>
      </div>
      <div className="flex flex-row items-center">
        <LilypadLogo size="micro" withText={true} showBeta={true} />
      </div>
    </div>
  );
}

// Component: CodePane
function CodePane({ code }: CodePaneProps) {
  return (
    <div className="border-border/60 border-b">
      <div className="max-h-64 overflow-y-auto">
        <AnalyticsCodeBlock code={code} language="python" className="rounded-none border-none" />
      </div>
    </div>
  );
}

// Component: TraceRow
function TraceRow({ trace, isSelected, onSelect }: TraceRowProps) {
  return (
    <div
      className={`flex w-full cursor-pointer text-xs ${
        isSelected ? "hover:bg-accent/50 bg-accent/30" : "hover:bg-muted/30"
      }`}
      onClick={() => onSelect(trace.id)}
    >
      <div className="border-border/20 w-[15%] flex-shrink-0 border-t px-2 py-2">
        {trace.version}
      </div>
      <div className="border-border/20 w-[15%] flex-shrink-0 border-t px-2 py-2">
        {trace.label === "pass" ? (
          <CheckCircle2 className="h-4 w-4 text-green-500" />
        ) : (
          <XCircle className="h-4 w-4 text-red-500" />
        )}
      </div>
      <div className="border-border/20 text-muted-foreground w-[25%] flex-shrink-0 border-t px-2 py-2">
        {trace.timestamp}
      </div>
      <div className="border-border/20 text-muted-foreground w-[20%] flex-shrink-0 border-t px-2 py-2">
        ${trace.cost.toFixed(4)}
      </div>
      <div className="border-border/20 text-muted-foreground w-[15%] flex-shrink-0 border-t px-2 py-2">
        {trace.tokens}
      </div>
    </div>
  );
}

// Component: TracesTable
function TracesTable({ traces, selectedTraceId, onSelectTrace }: TracesTableProps) {
  return (
    <div className="border-border/60 border-r md:w-1/2">
      <div className="border-border/60 bg-muted border-b px-4 py-2">
        <h3 className="text-sm font-semibold">Traces</h3>
      </div>
      <div className="max-h-64 overflow-y-auto">
        {/* Headers - Flexbox Row */}
        <div className="bg-muted/50 sticky top-0 flex w-full text-xs">
          <div className="text-muted-foreground w-[15%] flex-shrink-0 px-4 py-2 font-medium">
            Version
          </div>
          <div className="text-muted-foreground w-[15%] flex-shrink-0 px-4 py-2 font-medium">
            Label
          </div>
          <div className="text-muted-foreground w-[25%] flex-shrink-0 px-4 py-2 font-medium">
            Time
          </div>
          <div className="text-muted-foreground w-[20%] flex-shrink-0 px-4 py-2 font-medium">
            Cost
          </div>
          <div className="text-muted-foreground w-[15%] flex-shrink-0 px-4 py-2 font-medium">
            Tokens
          </div>
        </div>

        {/* Rows */}
        {traces.map((trace) => (
          <TraceRow
            key={trace.id}
            trace={trace}
            isSelected={selectedTraceId === trace.id}
            onSelect={onSelectTrace}
          />
        ))}
      </div>
    </div>
  );
}

// Component: MessagesPane
function MessagesPane({ input, output }: MessagesPaneProps) {
  return (
    <div className="flex flex-col md:w-1/2">
      <div className="border-border/60 bg-muted border-b px-4 py-2">
        <h3 className="text-sm font-semibold">Messages</h3>
      </div>
      <div className="flex max-h-64 flex-col gap-3 overflow-y-auto p-2">
        <MessageCard type="user" content={input} />
        <MessageCard type="assistant" content={output} />
      </div>
    </div>
  );
}

// Main Component
export function LilypadDemo() {
  // Sample trace data
  const traces: Trace[] = [
    {
      id: "trace_1",
      version: 2,
      label: "pass",
      timestamp: "1 min ago",
      promptTemplate: "Answer in one word: {question}",
      question: "What is the capital of France?",
      output: "Paris",
      cost: 0.0012,
      tokens: 24,
    },
    {
      id: "trace_2",
      version: 2,
      label: "pass",
      timestamp: "2 mins ago",
      promptTemplate: "Answer in one word: {question}",
      question: "What is the capital of Italy?",
      output: "Rome",
      cost: 0.0011,
      tokens: 22,
    },
    {
      id: "trace_3",
      version: 1,
      label: "fail",
      timestamp: "1 hr ago",
      promptTemplate: "Answer this question: {question}",
      question: "What is the capital of Spain?",
      output: "The capital of Spain is Madrid.",
      cost: 0.0018,
      tokens: 36,
    },
    {
      id: "trace_4",
      version: 1,
      label: "fail",
      timestamp: "1 hr ago",
      promptTemplate: "Answer this question: {question}",
      question: "What is the capital of China?",
      output: "The capital of China is Beijing.",
      cost: 0.0019,
      tokens: 38,
    },
  ];

  // State for selected trace
  const [selectedTraceId, setSelectedTraceId] = useState<string>(traces[0].id);

  // Get the selected trace
  const selectedTrace = traces.find((trace) => trace.id === selectedTraceId) || traces[0];

  // Format the input message from the template and question
  const formatInputMessage = (trace: Trace) => {
    return trace.promptTemplate.replace("{question}", trace.question);
  };

  // Generate code example based on selected trace
  const getCodeExample = (trace: Trace) => {
    const preSubstitution = `import lilypad
from mirascope import llm
lilypad.configure(auto_llm=True)

@lilypad.trace(versioning="automatic") # [!code highlight]
@llm.call(provider="$PROVIDER", model="$MODEL")
def answer_question(question: str) -> str:
    return f"${trace.promptTemplate}" # [!code highlight]

answer_question("${trace.question}")`;
    const { provider } = useProvider();
    return replaceProviderVariables(preSubstitution, provider);
  };

  return (
    <div className="border-border/60 bg-background w-full max-w-3xl overflow-hidden rounded-lg border backdrop-blur-sm">
      <Header functionName="answer_question" version={selectedTrace.version} />
      <CodePane code={getCodeExample(selectedTrace)} />

      <div className="-mt-2 flex flex-col md:flex-row">
        <TracesTable
          traces={traces}
          selectedTraceId={selectedTraceId}
          onSelectTrace={setSelectedTraceId}
        />
        <MessagesPane input={formatInputMessage(selectedTrace)} output={selectedTrace.output} />
      </div>
    </div>
  );
}
