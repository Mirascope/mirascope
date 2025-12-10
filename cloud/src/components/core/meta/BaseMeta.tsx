/**
 * BaseMeta Component
 *
 * Shared base implementation for CoreMeta and RouteMeta components.
 * Handles:
 * - Serialized metadata extraction in prerendering mode
 * - HeadManager integration in client mode
 */

import { useEffect } from "react";
import { environment } from "@/src/lib/content/environment";
import { extractMetadata, serializeMetadata } from "./utils";
import { HeadManager } from "./HeadManager";
import type { MetadataSource } from "./HeadManager";

export interface BaseMetaProps {
  children?: React.ReactNode;
  metaType: MetadataSource;
  dataAttribute: string;
  testId: string;
}

export function BaseMeta({ children, metaType, dataAttribute, testId }: BaseMetaProps) {
  // In prerendering mode, we only output a hidden div with serialized metadata
  if (environment.isPrerendering) {
    // Extract metadata
    const metadata = extractMetadata(children);

    // Serialize metadata for extraction during build
    const serializedMetadata = serializeMetadata(metadata);

    // Create data attribute with dynamic name
    const divProps: Record<string, any> = {
      [dataAttribute]: serializedMetadata,
      style: { display: "none" },
      "data-testid": testId,
    };

    return <div {...divProps} />;
  }

  // In client mode, register with HeadManager
  useEffect(() => {
    if (typeof document !== "undefined") {
      const metadata = extractMetadata(children);
      HeadManager.update(metaType, metadata);
    }
  }, [children, metaType]);

  // Don't render anything in the DOM
  return null;
}
