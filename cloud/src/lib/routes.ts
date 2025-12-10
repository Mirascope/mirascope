import { type Product, productKey } from "@/src/lib/content/spec";

// Handle type compatibility with TanStack Router paths
// Using type assertion to match what the router expects
export function getProductRoute(product: Product): any {
  return "/docs/" + productKey(product);
}

// Function to create a section route with the dynamic path pattern
export function getSectionRoute(_product: Product, _section: string): any {
  return `/docs/${productKey(_product)}/$`;
}

// Function to create params for a section route
export function getSectionParams(product: Product, section: string): any {
  return { product, _splat: section } as any;
}

// Function to create a blog post route
export function getBlogRoute(_slug: string): any {
  return "/blog/$slug" as any;
}

// Function to create params for a blog post route
export function getBlogParams(slug: string): { slug: string } {
  return { slug };
}
