import ReactJsonView from "@uiw/react-json-view";
import { vscodeTheme } from "@uiw/react-json-view/vscode";
import { githubLightTheme } from "@uiw/react-json-view/githubLight";
import { useTheme } from "@/app/components/blocks/theme-provider";

interface JsonViewProps {
  value: object;
  className?: string;
}

export function JsonView({ value, className }: JsonViewProps) {
  const { current } = useTheme();
  const theme = current === "dark" ? vscodeTheme : githubLightTheme;

  return (
    <ReactJsonView
      value={value}
      className={className}
      style={{
        ...theme,
        overflow: "auto",
        "--w-rjv-background-color": "hsl(var(--muted))",
      } as React.CSSProperties}
      displayDataTypes={false}
      displayObjectSize={false}
    />
  );
}
