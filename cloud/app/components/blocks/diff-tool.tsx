import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import { Button } from "@/app/components/ui/button";
import { diffArrays } from "diff";
import { useState } from "react";
import type { BuiltinLanguage, BundledLanguage } from "shiki";

const PLACEHOLDER = Symbol("placeholder");

// Define types for diff data
type DiffType = "modified" | "removed" | "added" | "unchanged";

interface DiffPart {
  value: string[];
  added?: boolean;
  removed?: boolean;
}

interface ProcessedDiffBlock {
  type: DiffType;
  oldValue: (string | symbol)[];
  newValue: (string | symbol)[];
}

/**
 * Process diffed lines into a more structured format for rendering
 */
const processDiffData = (diffedLines: DiffPart[]): ProcessedDiffBlock[] => {
  const result: ProcessedDiffBlock[] = [];
  let i = 0;

  while (i < diffedLines.length) {
    const current = diffedLines[i];

    if (
      current.removed &&
      i + 1 < diffedLines.length &&
      diffedLines[i + 1].added
    ) {
      // This is a modification (paired removal and addition)
      const oldValue = current.value;
      const newValue = diffedLines[i + 1].value;
      const maxLength = Math.max(oldValue.length, newValue.length);

      result.push({
        type: "modified",
        oldValue: oldValue.concat(
          Array(maxLength - oldValue.length).fill(PLACEHOLDER),
        ),
        newValue: newValue.concat(
          Array(maxLength - newValue.length).fill(PLACEHOLDER),
        ),
      });
      i += 2; // Skip the next item as we've processed it
    } else if (current.removed) {
      // This is a removal
      const oldValue = current.value;
      const newValue = Array(oldValue.length).fill(PLACEHOLDER);
      result.push({
        type: "removed",
        oldValue: oldValue as (string | symbol)[],
        newValue: newValue as (string | symbol)[],
      });
      i++;
    } else if (current.added) {
      // This is an addition
      const newValue = current.value;
      const oldValue = Array(newValue.length).fill(PLACEHOLDER);
      result.push({
        type: "added",
        oldValue: oldValue as (string | symbol)[],
        newValue: newValue as (string | symbol)[],
      });
      i++;
    } else {
      // This is an unchanged line
      result.push({
        type: "unchanged",
        oldValue: current.value,
        newValue: current.value,
      });
      i++;
    }
  }

  return result;
};

const getCommentSyntax = (
  lang: BuiltinLanguage,
  type: "add" | "remove" | "highlight",
): string => {
  // Different comment syntaxes for different languages
  let commentSyntax: string;
  if (type === "add") {
    commentSyntax = "[!code ++]";
  } else if (type === "remove") {
    commentSyntax = "[!code --]";
  } else {
    commentSyntax = "[!code highlight]";
  }
  switch (lang.toLowerCase()) {
    case "html":
    case "xml":
    case "svg":
    case "markdown":
    case "md":
      return `<!-- ${commentSyntax} -->`;
    case "css":
    case "scss":
    case "less":
      return `/* ${commentSyntax} */`;
    case "python":
    case "ruby":
    case "shell":
    case "bash":
    case "sh":
    case "yaml":
    case "yml":
      return `# ${commentSyntax}`;
    case "sql":
      return `--  ${commentSyntax}`;
    default:
      // Default to C-style comments (JavaScript, TypeScript, Java, C, C++, etc.)
      return `// ${commentSyntax}`;
  }
};

/**
 * Add line highlighting using Shiki's [!code highlight] comments
 */
const addHighlightComments = (
  lines: string[],
  lineHighlights: Record<number, string>,
  language: BuiltinLanguage,
): string => {
  const addCommentSyntax = getCommentSyntax(language, "add");
  const removeCommentSyntax = getCommentSyntax(language, "remove");
  const highlightCommentSyntax = getCommentSyntax(language, "highlight");
  return lines
    .map((line, index) => {
      // Line numbers are 1-based
      const lineNumber = index + 1;
      if (lineHighlights[lineNumber]) {
        if (lineHighlights[lineNumber] === "add") {
          return `${line} ${addCommentSyntax}`;
        } else if (lineHighlights[lineNumber] === "remove") {
          return `${line} ${removeCommentSyntax}`;
        } else {
          return `${line} ${highlightCommentSyntax}`;
        }
      }
      return line;
    })
    .join("\n");
};

interface CodeBlockWithLineNumbersSideBySideProps {
  diffedLines: DiffPart[];
  language?: BundledLanguage;
}

const CodeBlockWithLineNumbersSideBySide = ({
  diffedLines,
  language = "typescript",
}: CodeBlockWithLineNumbersSideBySideProps) => {
  const processedData = processDiffData(diffedLines);

  const renderColumn = (side: "before" | "after") => {
    let lineNumber = 0;
    const codeLines: string[] = [];
    const lineHighlights: Record<number, string> = {};

    processedData.forEach((block) => {
      const lines = side === "before" ? block.oldValue : block.newValue;

      lines.forEach((line) => {
        if (line !== PLACEHOLDER) {
          lineNumber++;
          codeLines.push(typeof line === "symbol" ? "" : line);
          if (
            (block.type === "modified" &&
              ((side === "before" &&
                !block.oldValue.every((v) => v === PLACEHOLDER)) ||
                (side === "after" &&
                  !block.newValue.every((v) => v === PLACEHOLDER)))) ||
            (block.type === "added" && side === "after") ||
            (block.type === "removed" && side === "before")
          ) {
            if (side === "before") {
              lineHighlights[lineNumber] = "remove";
            } else if (side === "after") {
              lineHighlights[lineNumber] = "add";
            }
          }
        } else {
          // Empty placeholder line
          codeLines.push("");
        }
      });
    });

    // Add the highlight comments and generate the final code string
    const highlightedCode = addHighlightComments(
      codeLines,
      lineHighlights,
      language,
    );

    return (
      <div className="w-full flex-1 overflow-x-auto">
        <CodeBlock code={highlightedCode} language={language} />
      </div>
    );
  };

  return (
    <div className="overflow-hidden rounded-md border font-mono text-sm">
      <div className="flex">
        {renderColumn("before")}
        <div className="w-px bg-gray-300"></div>
        {renderColumn("after")}
      </div>
    </div>
  );
};

interface CodeBlockWithLineNumbersAndHighlightsProps {
  diffedLines: DiffPart[];
  language?: BundledLanguage;
}

interface LineNumberMapping {
  old: number | null;
  new: number | null;
}

interface DiffPart {
  value: string[];
  removed?: boolean;
  added?: boolean;
}

interface CodeBlockWithLineNumbersAndHighlightsProps {
  diffedLines: DiffPart[];
  language?: BuiltinLanguage;
}

const processUnifiedDiffWithDualLineNumbers = (diffedLines: DiffPart[]) => {
  const codeLines: string[] = [];
  const lineHighlights: Record<number, string> = {};
  let oldLineNumber = 0;
  let newLineNumber = 0;
  const lineNumberMapping: LineNumberMapping[] = [];

  // First, flatten all diffedLines to handle hunks correctly
  const allLines: { text: string; removed?: boolean; added?: boolean }[] = [];

  diffedLines.forEach((part) => {
    part.value.forEach((line) => {
      allLines.push({
        text: line,
        removed: part.removed,
        added: part.added,
      });
    });
  });

  // Process each line
  allLines.forEach((line, index) => {
    // Add the line to the code display
    codeLines.push(line.text);

    // Update line numbers and mapping
    if (line.removed) {
      oldLineNumber++;
      lineNumberMapping.push({ old: oldLineNumber, new: null });
      lineHighlights[index + 1] = "remove";
    } else if (line.added) {
      newLineNumber++;
      lineNumberMapping.push({ old: null, new: newLineNumber });
      lineHighlights[index + 1] = "add";
    } else {
      // Unchanged lines
      oldLineNumber++;
      newLineNumber++;
      lineNumberMapping.push({ old: oldLineNumber, new: newLineNumber });
    }
  });

  return { codeLines, lineHighlights, lineNumberMapping };
};
const CodeBlockWithLineNumbersAndHighlights = ({
  diffedLines,
  language = "python",
}: CodeBlockWithLineNumbersAndHighlightsProps) => {
  // Generate the unified code view

  const { codeLines, lineHighlights } =
    processUnifiedDiffWithDualLineNumbers(diffedLines);
  // Add the highlight comments and generate the final code string
  const highlightedCode = addHighlightComments(
    codeLines,
    lineHighlights,
    language,
  );
  return (
    <CodeBlock
      code={highlightedCode}
      language={language}
      className="unified-diff border-0"
    />
  );
};

interface DiffToolProps {
  incomingCodeBlock: string;
  baseCodeBlock: string;
  language?: BundledLanguage;
}

export const DiffTool = ({
  incomingCodeBlock,
  baseCodeBlock,
  language = "typescript",
}: DiffToolProps) => {
  const [mode, setMode] = useState<"split" | "unified">("unified");

  const handleModeChange = (checked: boolean) => {
    setMode(checked ? "split" : "unified");
  };

  let diffed: DiffPart[] | null = null;
  if (incomingCodeBlock && baseCodeBlock) {
    const firstCode = incomingCodeBlock.split("\n");
    const secondCode = baseCodeBlock.split("\n");
    diffed = diffArrays(firstCode, secondCode);
  }

  return (
    <>
      {diffed && (
        <div className="flex flex-col gap-2">
          <div className="shrink-0">
            <div className="bg-muted inline-flex items-center gap-0.5 rounded-lg p-1">
              <Button
                variant={mode === "unified" ? "default" : "ghost"}
                size="sm"
                className="flex items-center gap-1"
                onClick={() => handleModeChange(false)}
              >
                <span>Unified</span>
              </Button>
              <Button
                variant={mode === "split" ? "default" : "ghost"}
                size="sm"
                className="flex items-center gap-1"
                onClick={() => handleModeChange(true)}
              >
                <span>Split</span>
              </Button>
            </div>
          </div>
          <div className="w-full grow-1">
            {mode === "unified" ? (
              <CodeBlockWithLineNumbersAndHighlights
                diffedLines={diffed}
                language={language}
              />
            ) : (
              <CodeBlockWithLineNumbersSideBySide
                diffedLines={diffed}
                language={language}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
};
