declare module "*.mdx" {
  import type { ProcessedMDX } from "@/app/lib/mdx/types";

  export const mdx: ProcessedMDX;
}
