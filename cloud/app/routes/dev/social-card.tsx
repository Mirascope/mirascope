import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { useState, useEffect, useRef, useCallback } from "react";

import DevLayout from "@/app/components/blocks/dev/dev-layout";
import LoadingContent from "@/app/components/blocks/loading-content";
import { getAllDevMeta } from "@/app/lib/content/virtual-module";
import {
  loadAssetsBrowser,
  renderSocialCardToDataUrl,
} from "@/app/lib/social-cards/render-browser";

export const Route = createFileRoute("/dev/social-card")({
  component: SocialCardPreview,
  loader: () => {
    const devPages = getAllDevMeta();
    return { devPages };
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
});

function SocialCardPreview() {
  const { devPages } = useLoaderData({ from: "/dev/social-card" });
  const [title, setTitle] = useState("Your Title Goes Here");
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const assetsRef = useRef<{
    font: ArrayBuffer;
    logo: string;
    background: string;
  } | null>(null);

  // Load assets once on mount
  useEffect(() => {
    loadAssetsBrowser()
      .then((assets) => {
        assetsRef.current = assets;
        // Generate initial preview
        return renderSocialCardToDataUrl(title, assets);
      })
      .then(setImageUrl)
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load assets");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Debounced preview generation
  const updatePreview = useCallback((newTitle: string) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (!assetsRef.current) return;

    setIsLoading(true);
    setError(null);

    debounceRef.current = setTimeout(() => {
      if (!assetsRef.current) return;

      renderSocialCardToDataUrl(newTitle, assetsRef.current)
        .then((dataUrl) => {
          setImageUrl(dataUrl);
          setIsLoading(false);
        })
        .catch((err: unknown) => {
          setError(
            err instanceof Error ? err.message : "Failed to generate preview",
          );
          setIsLoading(false);
        });
    }, 150); // Faster debounce since it's client-side
  }, []);

  // Generate preview on title change
  useEffect(() => {
    if (assetsRef.current) {
      updatePreview(title);
    }

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [title, updatePreview]);

  return (
    <DevLayout devPages={devPages}>
      <div className="container">
        <h1 className="mb-6 text-3xl font-bold">Social Card Preview</h1>

        <p className="mb-6 text-gray-600">
          Preview how social cards will look. Edit the title to see the card
          update in real-time.
        </p>

        <div className="mb-6">
          <div className="mb-2 flex items-center justify-between">
            <label htmlFor="title" className="font-medium">
              Title
            </label>
            <span className="text-sm text-gray-500">
              {title.length} characters
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

        <div className="flex justify-center">
          <div
            className="relative overflow-hidden rounded-lg border bg-gray-50"
            style={{ width: "600px", height: "315px" }}
          >
            {error ? (
              <div className="flex h-full items-center justify-center text-red-500">
                {error}
              </div>
            ) : imageUrl ? (
              <>
                <img
                  src={imageUrl}
                  alt="Social card preview"
                  className="h-full w-full object-cover"
                />
                {isLoading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-white/50">
                    <LoadingContent
                      spinnerClassName="h-8 w-8"
                      fullHeight={false}
                    />
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-full items-center justify-center">
                <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
              </div>
            )}
          </div>
        </div>

        <p className="mt-4 text-center text-sm text-gray-500">
          Preview shows SVG output from satori. Production uses additional
          PNG/WebP conversion.
        </p>
      </div>
    </DevLayout>
  );
}
