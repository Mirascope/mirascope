import { createFileRoute } from "@tanstack/react-router";
import { NotFound } from "@/app/components/not-found";
import { blogPostContentLoader } from "@/app/lib/content/content-loader";
import { BlogPostPage } from "@/app/components/blog-post-page";

export const Route = createFileRoute("/blog/$slug")({
  ssr: false,
  head: (ctx) => {
    // todo(sebastian): simplify and add other SEO metadata
    const meta = ctx.loaderData?.meta;
    if (!meta) {
      return {};
    }
    return {
      meta: [
        { title: meta.title },
        { name: "description", content: meta.description },
      ],
    };
  },
  loader: blogPostContentLoader(),
  component: BlogPost,
});

function BlogPost() {
  const post = Route.useLoaderData();

  if (!post) {
    return <NotFound />;
  }

  return <BlogPostPage post={post} slug={post.meta.slug} />;
}
