import { type ProductName } from "./content/spec";

// Type guard to check if a string is a valid product name
export function isValidProductName(productName: string): productName is ProductName {
  return productName === "mirascope" || productName === "lilypad";
}

// Type aliases for valid static paths in the router
export type ValidStaticPath =
  | "/"
  | "/blog"
  | "/docs"
  | "/docs/mirascope"
  | "/docs/lilypad"
  | "/privacy"
  | "/terms";

// Type aliases for valid dynamic paths in the router
export type ValidDynamicPath =
  | "/blog/$slug"
  | "/docs/$"
  | "/docs/$product/$"
  | "/docs/$product/api/$"
  | "/docs/$product/guides/$";

// Combine all valid paths for use in the router
export type ValidPath = ValidStaticPath | ValidDynamicPath;
