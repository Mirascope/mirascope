import { createFileRoute } from "@tanstack/react-router";
import { getAllBlogMeta } from "@/app/lib/content/meta";
import { BlogPage } from "../components/blog-page";

export const Route = createFileRoute("/blog/")({
  // todo(sebastian): simplify and add other SEO metadata
  head: () => ({
    meta: [
      { title: "Blog" },
      {
        name: "description",
        content:
          "The latest news, updates, and insights about Mirascope and LLM application development.",
      },
    ],
  }),
  component: () => {
    const posts = getAllBlogMeta();
    return <BlogPage posts={posts} />;
  },
});
