import { CopyButton } from "@/mirascope-ui/blocks/copy-button";
import {
  highlightCode,
  stripHighlightMarkers,
  type HighlightResult,
  initialHighlight,
} from "@/mirascope-ui/lib/code-highlight";
import { cn } from "@/mirascope-ui/lib/utils";
import { useEffect, useRef, useState } from "react";

interface CodeBlockProps {
  code: string;
  language?: string;
  meta?: string;
  className?: string;
  showLineNumbers?: boolean;
  onCopy?: (content: string) => void;
}

export function CodeBlock({
  code,
  language = "text",
  meta = "",
  className = "",
  showLineNumbers = true,
  onCopy,
}: CodeBlockProps) {
  const [highlightedCode, setHighlightedCode] = useState<HighlightResult>(
    initialHighlight(code, language, meta)
  );
  const codeRef = useRef<HTMLDivElement>(null);
  const [isSmallBlock, setIsSmallBlock] = useState<boolean>(false);

  // Calculate dynamic padding for line numbers
  const lineCount = code.split("\n").length;
  const extraPadding = 1 + Math.max(0, Math.floor(Math.log10(lineCount))) * 0.2;
  const lineNumberPadding = `${extraPadding}rem`;

  // Base styles for code block container
  const codeBlockBaseStyles =
    "code-block-wrapper border-card relative m-0 mb-2 rounded-md overflow-hidden border p-0 text-xs group";

  useEffect(() => {
    // If code changed, use the initial highlighter for the first render
    const result = initialHighlight(code, language, meta);
    setHighlightedCode(result);

    // Only do async highlighting if the initial highlight didn't already do a full highlight
    if (!result.highlighted) {
      async function highlight() {
        try {
          setHighlightedCode(await highlightCode(code, language, meta));
        } catch (error) {
          console.error("Error highlighting code:", error);
          // Leave the fallback code
        }
      }
      highlight();
    }
  }, [code, language, meta]);

  // Check if code block is small after rendering
  useEffect(() => {
    if (codeRef.current) {
      // Get the height of the code block
      const height = codeRef.current.clientHeight;
      // Consider blocks less than 100px as small
      setIsSmallBlock(height < 100);
    }
  }, [highlightedCode]);

  return (
    <div
      ref={codeRef}
      className={cn(codeBlockBaseStyles, `${showLineNumbers && "show-line-numbers"}`, className)}
      style={{ "--line-number-padding": lineNumberPadding } as React.CSSProperties}
    >
      {/* Buttons - positioned based on block size */}
      <div
        className={cn(
          "absolute z-10 opacity-0 transition-opacity group-hover:opacity-100 max-sm:opacity-80 sm:opacity-0",
          isSmallBlock ? "top-1/2 right-3 flex -translate-y-1/2 space-x-1" : "top-3 right-3"
        )}
      >
        <CopyButton content={stripHighlightMarkers(code)} onCopy={onCopy} />
      </div>

      <div className="highlight-container w-full overflow-auto">
        <div
          className="text-sm [&_code]:block [&_code]:w-fit [&_code]:min-w-full [&>pre]:overflow-x-auto [&>pre]:py-3 [&>pre]:pr-5 [&>pre]:pl-4"
          dangerouslySetInnerHTML={{ __html: highlightedCode.themeHtml }}
        />
      </div>
    </div>
  );
}
