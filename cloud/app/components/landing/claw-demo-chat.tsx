import { FileTextIcon } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import {
  Message,
  MessageContent,
  MessageResponse,
} from "@/app/components/ai-elements/message";
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from "@/app/components/ai-elements/reasoning";

const USER_MSG = "Help me build an invoice processor for invoices like this:";
const THINKING =
  "I'll create a claw that extracts structured data from invoices — vendor, amount, due date, and line items — and outputs validated JSON.";
const ASSISTANT_MSG =
  "Done! I've created **Invoice Processor v1** with:\n\n- **Input:** PDF or image upload\n- **Output:** Structured JSON (vendor, amount, due date, line items)\n- **Validation:** Cross-checks totals against line items\n\nReady to deploy?";

type Step = "idle" | "user" | "thinking" | "response" | "done";

interface ClawDemoChatProps {
  isActive: boolean;
  onComplete?: () => void;
}

export function ClawDemoChat({ isActive, onComplete }: ClawDemoChatProps) {
  const [step, setStep] = useState<Step>("idle");
  const [reasoningOpen, setReasoningOpen] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isActive) {
      setStep("idle");
      return;
    }
    setStep("idle");
    const t = setTimeout(() => setStep("user"), 400);
    return () => clearTimeout(t);
  }, [isActive]);

  useEffect(() => {
    if (!isActive) return;
    let t: ReturnType<typeof setTimeout>;
    switch (step) {
      case "user":
        t = setTimeout(() => setStep("thinking"), 1800);
        break;
      case "thinking":
        t = setTimeout(() => setStep("response"), 2500);
        break;
      case "response":
        t = setTimeout(() => setStep("done"), 3000);
        break;
      case "done":
        t = setTimeout(() => onComplete?.(), 2000);
        break;
    }
    return () => clearTimeout(t!);
  }, [step, isActive, onComplete]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const scrollParent = el.closest("[data-demo-scroll]") ?? el.parentElement;
    if (scrollParent) {
      scrollParent.scrollTo({
        top: scrollParent.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [step]);

  const showUser = step !== "idle";
  const showThinking =
    step === "thinking" || step === "response" || step === "done";
  const showResponse = step === "response" || step === "done";

  return (
    <div
      ref={containerRef}
      className="flex flex-col gap-2.5 p-4 text-slate-900 dark:text-foreground"
    >
      {showUser && (
        <Message from="user">
          <MessageContent className="text-xs">
            <MessageResponse className="text-xs [&_p]:my-0 [&_strong]:font-bold">
              {USER_MSG}
            </MessageResponse>
            <div className="flex items-center gap-1.5 rounded-md bg-white/15 px-2 py-1.5 text-[11px] text-white/90">
              <FileTextIcon className="size-3.5 shrink-0" />
              <span className="truncate">invoice_march.pdf</span>
            </div>
          </MessageContent>
        </Message>
      )}

      {showThinking && (
        <Reasoning
          open={reasoningOpen}
          onOpenChange={setReasoningOpen}
          duration={1}
        >
          <ReasoningTrigger className="text-xs text-slate-500 hover:text-slate-700 dark:text-muted-foreground dark:hover:text-foreground" />
          <ReasoningContent className="text-xs text-slate-600 dark:text-foreground">
            {THINKING}
          </ReasoningContent>
        </Reasoning>
      )}

      {showResponse && (
        <Message from="assistant">
          <MessageContent className="text-xs !text-slate-900 dark:!text-foreground">
            <MessageResponse className="text-xs [&_p]:my-0.5 [&_p]:leading-snug [&_li]:my-0 [&_strong]:font-bold">
              {ASSISTANT_MSG}
            </MessageResponse>
          </MessageContent>
        </Message>
      )}

      {showUser && !showResponse && (
        <div className="flex items-center gap-1.5 px-1 text-xs text-slate-400 dark:text-muted-foreground">
          <span className="flex gap-0.5">
            <span className="inline-block size-1.5 animate-bounce rounded-full bg-slate-400 dark:bg-muted-foreground [animation-delay:0ms]" />
            <span className="inline-block size-1.5 animate-bounce rounded-full bg-slate-400 dark:bg-muted-foreground [animation-delay:150ms]" />
            <span className="inline-block size-1.5 animate-bounce rounded-full bg-slate-400 dark:bg-muted-foreground [animation-delay:300ms]" />
          </span>
        </div>
      )}
    </div>
  );
}
