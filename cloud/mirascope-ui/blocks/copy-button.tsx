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
    navigator.clipboard.writeText(content);
    setIsCopied(true);
    toast.success("Successfully copied to clipboard");
    setTimeout(() => setIsCopied(false), 2000);
    onCopy?.(content);
  };
  return (
    <button
      className="bg-background hover:bg-muted relative cursor-pointer rounded-md border p-1.5"
      onClick={copyToClipboard}
      aria-label="Copy code"
      title="Copy code"
    >
      {isCopied ? <Check className="size-4" /> : <Copy className="size-4" />}
    </button>
  );
};
