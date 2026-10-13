import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export interface CopyButtonProps {
  content: string;
  onCopy?: (content: string) => void;
}

export const CopyButton = ({ content, onCopy }: CopyButtonProps) => {
  const [isCopied, setIsCopied] = useState<boolean>(false);
  const copyToClipboard = () => {
    void navigator.clipboard.writeText(content);
    setIsCopied(true);
    toast.success("Successfully copied to clipboard");
    setTimeout(() => setIsCopied(false), 2000);
    onCopy?.(content);
  };
  return (
    <button
      className="bg-white dark:bg-background hover:bg-slate-100 dark:hover:bg-muted text-slate-600 dark:text-foreground relative cursor-pointer rounded-md border border-slate-300 dark:border-border p-1.5"
      onClick={copyToClipboard}
      aria-label="Copy code"
      title="Copy code"
    >
      {isCopied ? <Check className="size-4" /> : <Copy className="size-4" />}
    </button>
  );
};
