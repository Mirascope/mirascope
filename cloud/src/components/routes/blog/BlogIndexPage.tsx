import { Link } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import { type BlogMeta } from "@/src/lib/content";
import { PageMeta, LoadingContent } from "@/src/components";
import { BlogPagination } from "./BlogPagination";

// Posts per page
const POSTS_PER_PAGE = 4;

/**
 * Blog layout component that provides the common structure for both the blog index and loading state
 */
interface BlogLayoutProps {
  children: ReactNode;
}

export function BlogLayout({ children }: BlogLayoutProps) {
  return (
    <div className="font-handwriting flex justify-center">
      <div className="mx-auto flex w-full max-w-[1800px] px-4 pt-6">
        <div className="min-w-0 flex-1">
          <div className="mx-auto max-w-5xl">
            <div className="mb-8 text-center">
              <h1 className="font-handwriting mb-4 text-center text-4xl font-bold">Blog</h1>
              <p className="text-foreground font-handwriting mx-auto max-w-2xl text-xl">
                The latest news, updates, and insights about
                <br />
                Mirascope and LLM application development.
              </p>
            </div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Blog loading component that shows a spinner while content is loading
 */
export function BlogLoadingState() {
  return (
    <BlogLayout>
      <div className="flex h-64 items-center justify-center">
        <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
      </div>
    </BlogLayout>
  );
}

interface BlogIndexPageProps {
  /**
   * Blog posts metadata
   */
  posts: BlogMeta[];
}

export function BlogIndexPage({ posts }: BlogIndexPageProps) {
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.ceil(posts.length / POSTS_PER_PAGE);

  // Get posts for the current page
  const startIdx = (currentPage - 1) * POSTS_PER_PAGE;
  const endIdx = startIdx + POSTS_PER_PAGE;
  const currentPosts = posts.slice(startIdx, endIdx);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <>
      <PageMeta
        title="Blog"
        description="The latest news, updates, and insights about Mirascope and LLM application development."
        type="website"
      />
      <BlogLayout>
        <div className="mb-10 min-h-[700px]">
          {posts.length === 0 ? (
            <div className="py-12 text-center">
              <h2 className="text-foreground text-xl font-medium">No posts found</h2>
              <p className="text-foreground mt-2">Check back soon for new content!</p>
            </div>
          ) : (
            <div className="grid min-h-[650px] grid-cols-1 gap-8 md:grid-cols-2">
              {currentPosts.map((post) => (
                <Link
                  key={post.slug}
                  to="/blog/$slug"
                  params={{ slug: post.slug }}
                  className="group block h-full cursor-pointer"
                >
                  <div className="bg-background border-border flex h-[320px] flex-col overflow-hidden rounded-lg border-1 shadow-sm transition-all duration-200 hover:shadow-lg">
                    <div className="flex h-full flex-col p-6">
                      <div>
                        <h3 className="group-hover:text-primary mb-2 text-xl font-semibold transition-colors">
                          {post.title}
                        </h3>
                        <p className="text-muted-foreground mb-4 text-sm select-none">
                          {post.date} · {post.readTime} · By {post.author}
                        </p>
                        <p className="text-foreground mb-4 line-clamp-3 font-sans select-none">
                          {post.description}
                        </p>
                      </div>
                      <span className="text-foreground group-hover:text-primary mt-auto font-medium transition-colors">
                        Read more
                      </span>
                    </div>
                  </div>
                </Link>
              ))}

              {/* Spacer elements to maintain grid layout when fewer than POSTS_PER_PAGE posts */}
              {[...Array(Math.max(0, POSTS_PER_PAGE - currentPosts.length))].map((_, index) => (
                <div key={`spacer-${index}`} className="invisible h-[320px] md:h-[320px]" />
              ))}
            </div>
          )}
        </div>

        {posts.length > 0 && (
          <div className="w-full border-t pt-4 pb-8">
            <BlogPagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          </div>
        )}
      </BlogLayout>
    </>
  );
}
