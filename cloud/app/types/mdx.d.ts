declare module "*.mdx" {
  import type { PreprocessedMDX } from "@/app/lib/mdx/types";

  const mdx: PreprocessedMDX;
  export default mdx;
}
