import { useState } from "react";
import { Button } from "@/app/components/ui/button";
import { Clipboard, Check } from "lucide-react";
import { useAnalytics } from "@/app/contexts/analytics";

interface CopyMarkdownButtonProps {
  content: string;
  itemId: string;
  contentType: "blog_markdown" | "document_markdown";
  className?: string;
}

export function CopyMarkdownButton({
  content,
  itemId,
  contentType,
  className = "",
}: CopyMarkdownButtonProps) {
  const analytics = useAnalytics();
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = () => {
    if (!content) {
      return;
    }

    navigator.clipboard
      .writeText(content)
      .then(() => {
        setIsCopied(true);
        setTimeout(() => {
          setIsCopied(false);
        }, 2000);

        analytics.trackEvent("select_content", {
          contentType,
          itemId,
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
