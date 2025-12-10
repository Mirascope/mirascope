/**
 * CoreMeta Component
 *
 * Defines site-wide metadata that remains consistent across all pages:
 * - Character encoding, viewport settings
 * - Favicon definitions
 * - Font preloading
 * - Web manifest links
 * - Other global meta tags
 */

import { BaseMeta } from "./BaseMeta";

export interface CoreMetaProps {
  children?: React.ReactNode;
}

export function CoreMeta({ children }: CoreMetaProps) {
  return (
    <BaseMeta
      children={children}
      metaType="core"
      dataAttribute="data-core-meta"
      testId="core-meta-serialized"
    />
  );
}

export default CoreMeta;
