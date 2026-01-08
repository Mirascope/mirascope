import type { ContentMeta, BlogMeta } from "@/app/lib/content/types";

declare module "virtual:content-meta" {
  export const blogPosts: BlogMeta[];
  export const allContent: ContentMeta[];
}
