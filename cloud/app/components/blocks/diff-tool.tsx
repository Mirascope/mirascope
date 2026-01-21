import { FileDiff } from "@pierre/diffs/react";
import { parseDiffFromFile } from "@pierre/diffs";
import type { FileContents, SupportedLanguages } from "@pierre/diffs";
import { Button } from "@/app/components/ui/button";
import { useMemo, useState } from "react";
import { useTheme } from "next-themes";

interface DiffToolProps {
  baseCode: string;
  newCode: string;
  language?: SupportedLanguages;
  baseName?: string;
  newName?: string;
}

export const DiffTool = ({
  baseCode,
  newCode,
  language = "python",
  baseName = "base",
  newName = "new",
}: DiffToolProps) => {
  const [mode, setMode] = useState<"unified" | "split">("unified");
  const { resolvedTheme } = useTheme();

  const fileDiff = useMemo(() => {
    const oldFile: FileContents = {
      name: baseName,
      contents: baseCode,
      lang: language,
    };
    const newFile: FileContents = {
      name: newName,
      contents: newCode,
      lang: language,
    };
    return parseDiffFromFile(oldFile, newFile);
  }, [baseCode, newCode, language, baseName, newName]);

  // Use the same themes as our code-highlight.ts
  const theme = useMemo(
    () => ({
      light: "github-light" as const,
      dark: "github-dark-default" as const,
    }),
    [],
  );

  return (
    <div className="flex flex-col gap-2">
      <div className="shrink-0">
        <div className="bg-muted inline-flex items-center gap-0.5 rounded-lg p-1">
          <Button
            variant={mode === "unified" ? "default" : "ghost"}
            size="sm"
            className="flex items-center gap-1"
            onClick={() => setMode("unified")}
          >
            <span>Unified</span>
          </Button>
          <Button
            variant={mode === "split" ? "default" : "ghost"}
            size="sm"
            className="flex items-center gap-1"
            onClick={() => setMode("split")}
          >
            <span>Split</span>
          </Button>
        </div>
      </div>
      <div className="diff-tool-container w-full grow overflow-hidden rounded-md border">
        <FileDiff
          fileDiff={fileDiff}
          options={{
            diffStyle: mode,
            theme,
            themeType: resolvedTheme === "dark" ? "dark" : "light",
            disableFileHeader: true,
            diffIndicators: "classic",
            lineDiffType: "word",
          }}
        />
      </div>
    </div>
  );
};
