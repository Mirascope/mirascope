import { useState } from "react";
import { Button } from "@/src/components/ui/button";
import { Clipboard, Check } from "lucide-react";
import analyticsManager from "@/src/lib/services/analytics";
import { type Product } from "@/src/lib/content/spec";

interface CopyMarkdownButtonProps {
  content: string;
  itemId: string;
  product?: Product;
  contentType: "blog_markdown" | "document_markdown";
  className?: string;
}

export function CopyMarkdownButton({
  content,
  itemId,
  product,
  contentType,
  className = "",
}: CopyMarkdownButtonProps) {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    if (!content) return;

    navigator.clipboard
      .writeText(content)
      .then(() => {
        setIsCopied(true);
        setTimeout(() => {
          setIsCopied(false);
        }, 2000);

        analyticsManager.trackCopyEvent({
          contentType,
          itemId,
          product,
        });
      })
      .catch((err) => {
        console.error("Failed to copy content: ", err);
      });
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleCopy}
      disabled={isCopied}
      className={`w-full ${className}`}
    >
      {isCopied ? (
        <>
          <Check className="mr-1 h-4 w-4" />
          Copied!
        </>
      ) : (
        <>
          <Clipboard className="mr-1 h-4 w-4" />
          Copy as Markdown
        </>
      )}
    </Button>
  );
}
