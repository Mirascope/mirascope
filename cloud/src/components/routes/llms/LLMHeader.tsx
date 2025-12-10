import { LLMContent } from "@/src/lib/content/llm-content";
import { Button } from "@/mirascope-ui/ui/button";
import { ButtonLink } from "@/mirascope-ui/ui/button-link";
import { ChevronDown, ChevronRight, Rocket, Clipboard } from "lucide-react";
import { formatTokenCount, tokenBadge } from "./utils";

interface LLMHeaderProps {
  content: LLMContent;
  level?: number;
  clickable?: boolean;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export default function LLMHeader({
  content,
  level = 1,
  clickable = false,
  isExpanded = false,
  onToggle,
}: LLMHeaderProps) {
  const titleElement = clickable ? (
    <button
      onClick={onToggle}
      className="text-muted-foreground hover:text-foreground flex cursor-pointer items-center gap-1 transition-colors"
    >
      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      <h3 className="text-foreground rounded-md px-2 py-1 text-left text-base font-bold">
        {content.title}
      </h3>
    </button>
  ) : (
    <h2 className={`px-2 text-left font-bold ${level === 1 ? "text-2xl" : "text-xl"}`}>
      {content.title}
    </h2>
  );

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between">
        <div className="flex min-w-0 items-start gap-1">
          {titleElement}
          {content.route && (
            <div className="flex-shrink-0 self-start">
              <ButtonLink href={content.route} variant="ghost" size="sm">
                <Rocket className="h-4 w-4" />
              </ButtonLink>
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={tokenBadge}>{formatTokenCount(content.tokenCount)} tokens</span>
          <Button
            onClick={() => navigator.clipboard.writeText(content.getContent())}
            variant="ghost"
            size="sm"
            className="text-xs"
          >
            <Clipboard className="h-4 w-4 sm:mr-1" />
            <span className="hidden sm:inline">Copy</span>
          </Button>
        </div>
      </div>
      {content.description && (
        <p className={`text-muted-foreground mt-2 px-2 text-sm ${clickable ? "ml-5" : ""}`}>
          {content.description}
        </p>
      )}
    </div>
  );
}
