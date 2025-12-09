import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { useState, useEffect, useRef, useCallback } from "react";
import DevLayout from "@/src/components/routes/dev/DevLayout";
import { environment } from "@/src/lib/content/environment";
import { getAllDevMeta, type ProductName } from "@/src/lib/content";
import { LoadingContent, ContentErrorHandler, PageMeta } from "@/src/components";

export const Route = createFileRoute("/social-card")({
  component: SocialCardPreview,
  loader: async () => {
    try {
      // Get all MDX-based dev pages for the sidebar
      const devPages = await getAllDevMeta();
      return { devPages };
    } catch (error) {
      console.error("Error loading dev pages:", error);
      return { devPages: [] };
    }
  },
  pendingComponent: () => {
    return (
      <DevLayout devPages={[]}>
        <div className="container">
          <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
        </div>
      </DevLayout>
    );
  },
  errorComponent: ({ error }) => {
    environment.onError(error);
    return (
      <ContentErrorHandler
        error={error instanceof Error ? error : new Error(String(error))}
        contentType="dev"
      />
    );
  },
});

// Helper interface for iframe communication
declare global {
  interface Window {
    updateSocialCard?: (title: string, product: ProductName) => void;
    SOCIAL_CARD_CONFIG?: {
      fontSizes: Array<{
        maxChars: number;
        fontSize: string;
        label: string;
      }>;
    };
  }
}

// Define font size config type
type FontSizeRule = { maxChars: number; fontSize: string; label: string };

function SocialCardPreview() {
  const { devPages } = useLoaderData({ from: "/dev/social-card" });
  const [title, setTitle] = useState("Your Title Goes Here");
  const [product, setProduct] = useState<ProductName>("mirascope");
  const [fontSizeRules, setFontSizeRules] = useState<FontSizeRule[]>([]);

  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [iframeLoaded, setIframeLoaded] = useState(false);

  // Update the card when form values change
  useEffect(() => {
    if (iframeLoaded && iframeRef.current?.contentWindow?.updateSocialCard) {
      iframeRef.current.contentWindow.updateSocialCard(title, product);
    }
  }, [title, product, iframeLoaded]);

  // Get the current font size rule that applies to this title length
  const getCurrentFontSizeRule = useCallback((): FontSizeRule | undefined => {
    return fontSizeRules.find((rule) => title.length <= rule.maxChars);
  }, [fontSizeRules, title.length]);

  // Handle iframe load event
  const handleIframeLoad = () => {
    setIframeLoaded(true);

    // Get font size config from iframe
    if (iframeRef.current?.contentWindow?.SOCIAL_CARD_CONFIG?.fontSizes) {
      setFontSizeRules(iframeRef.current.contentWindow.SOCIAL_CARD_CONFIG.fontSizes);
    }

    // Apply initial values
    if (iframeRef.current?.contentWindow?.updateSocialCard) {
      iframeRef.current.contentWindow.updateSocialCard(title, product);
    }
  };

  return (
    <>
      <PageMeta title="Social Card Preview" description="Preview and test social card designs" />
      <DevLayout devPages={devPages}>
        <div className="container">
          <h1 className="mb-6 text-3xl font-bold">Social Card Preview</h1>

          <p className="mb-6 text-gray-600">
            This page lets you preview how social cards will look. Edit the title to see the card
            update in real-time. Useful for iterating on the social-card.html file to preview
            changes to social cards and testing font sizing rules.
          </p>

          <div className="mb-6">
            <div className="mb-2 flex items-center justify-between">
              <label htmlFor="title" className="font-medium">
                Title
              </label>
              <span className="text-sm text-gray-500">
                {title.length} characters
                {getCurrentFontSizeRule() &&
                  ` - ${getCurrentFontSizeRule()?.fontSize} (${getCurrentFontSizeRule()?.label})`}
              </span>
            </div>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full rounded-md border px-3 py-2"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="product" className="mb-2 block font-medium">
              Product
            </label>
            <select
              id="product"
              value={product}
              onChange={(e) => setProduct(e.target.value as ProductName)}
              className="w-full rounded-md border px-3 py-2"
            >
              <option value="mirascope">Mirascope</option>
              <option value="lilypad">Lilypad</option>
            </select>
          </div>

          <div className="flex justify-center">
            <div
              className="overflow-hidden rounded-lg border bg-gray-50"
              style={{ width: "600px", height: "315px" }}
            >
              <div
                className="origin-top-left scale-50 transform"
                style={{ width: "200%", height: "200%" }}
              >
                <iframe
                  ref={iframeRef}
                  id="social-card-iframe"
                  src="/dev/social-card.html"
                  className="border-0"
                  style={{ width: "1200px", height: "630px" }}
                  title="Social Card Preview"
                  onLoad={handleIframeLoad}
                />
              </div>
            </div>
          </div>
        </div>
      </DevLayout>
    </>
  );
}
