import { createFileRoute } from "@tanstack/react-router";

import { BlogPage } from "@/app/components/blog-page";
import { getAllBlogMeta } from "@/app/lib/content/virtual-module";
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

export const Route = createFileRoute("/blog/")({
  head: createStaticRouteHead("/blog/"),
  component: () => {
    const posts = getAllBlogMeta();
    return <BlogPage posts={posts} />;
  },
});
