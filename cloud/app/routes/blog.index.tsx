import { createFileRoute } from "@tanstack/react-router";
import { getAllBlogMeta } from "@/app/lib/content/virtual-module";
import { BlogPage } from "@/app/components/blog-page";
import { createPageHead } from "@/app/lib/seo/head";

export const Route = createFileRoute("/blog/")({
  head: () =>
    createPageHead({
      route: "/blog",
      title: "Blog",
      description:
        "The latest news, updates, and insights about Mirascope and LLM application development.",
    }),
  component: () => {
    const posts = getAllBlogMeta();
    return <BlogPage posts={posts} />;
  },
});
