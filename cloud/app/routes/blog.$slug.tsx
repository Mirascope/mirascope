import { createFileRoute } from "@tanstack/react-router";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  BLOG_MODULE_MAP,
  getAllBlogMeta,
} from "@/app/lib/content/virtual-module";
import { BlogPostPage } from "@/app/components/blog-post-page";

export const Route = createFileRoute("/blog/$slug")(
  createContentRouteConfig("/blog/$slug", {
    getMeta: getAllBlogMeta,
    moduleMap: BLOG_MODULE_MAP,
    prefix: "blog",
    component: BlogPostPage,
  }),
);
