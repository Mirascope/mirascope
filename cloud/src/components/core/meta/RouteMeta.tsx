/**
 * RouteMeta Component
 *
 * Defines page-specific metadata that changes with each route:
 * - Page title
 * - Description
 * - Open Graph/social sharing metadata
 * - Structured data
 * - Other route-specific meta tags
 */

import { BaseMeta } from "./BaseMeta";

export interface RouteMetaProps {
  children?: React.ReactNode;
}

export function RouteMeta({ children }: RouteMetaProps) {
  return (
    <BaseMeta
      children={children}
      metaType="route"
      dataAttribute="data-route-meta"
      testId="route-meta-serialized"
    />
  );
}

export default RouteMeta;
