import { Link } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import { type BlogMeta } from "@/app/lib/content/types";
import LoadingContent from "@/app/components/blocks/loading-content";

import { useIsMobile } from "@/app/hooks/is-mobile";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/app/components/ui/pagination";
import { ChevronLeft, ChevronRight } from "lucide-react";

export interface BlogPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

function BlogPagination({
  currentPage,
  totalPages,
  onPageChange,
}: BlogPaginationProps) {
  const isMobile = useIsMobile();

  // Logic to determine which page numbers to show
  const renderPageNumbers = () => {
    const items = [];
    // Show fewer pages on mobile
    const delta = isMobile ? 0 : 3;

    // Always include first page
    items.push(
      <PaginationItem key={1}>
        <PaginationLink
          onClick={() => onPageChange(1)}
          isActive={currentPage === 1}
          className="cursor-pointer"
        >
          1
        </PaginationLink>
      </PaginationItem>,
    );

    // Add ellipsis if needed between first page and delta range
    if (currentPage > 2 + delta) {
      items.push(
        <PaginationItem key="ellipsis-1">
          <PaginationEllipsis />
        </PaginationItem>,
      );
    }

    // Add pages around current page based on delta
    for (
      let i = Math.max(2, currentPage - delta);
      i <= Math.min(totalPages - 1, currentPage + delta);
      i++
    ) {
      // Skip if already added as first or last page
      if (i === 1 || i === totalPages) continue;

      items.push(
        <PaginationItem key={i}>
          <PaginationLink
            onClick={() => onPageChange(i)}
            isActive={currentPage === i}
            className="cursor-pointer"
          >
            {i}
          </PaginationLink>
        </PaginationItem>,
      );
    }

    // Add ellipsis if needed between delta range and last page
    if (currentPage < totalPages - 1 - delta) {
      items.push(
        <PaginationItem key="ellipsis-2">
          <PaginationEllipsis />
        </PaginationItem>,
      );
    }

    // Always include last page if there's more than one page
    if (totalPages > 1) {
      items.push(
        <PaginationItem key={totalPages}>
          <PaginationLink
            onClick={() => onPageChange(totalPages)}
            isActive={currentPage === totalPages}
            className="cursor-pointer"
          >
            {totalPages}
          </PaginationLink>
        </PaginationItem>,
      );
    }

    return items;
  };

  // Custom Previous button that's just an arrow on mobile
  const CustomPrev = () => {
    if (isMobile) {
      return (
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className={`flex h-9 w-9 items-center justify-center rounded-md border ${
            currentPage === 1
              ? "pointer-events-none opacity-50"
              : "hover:bg-muted cursor-pointer"
          }`}
          aria-label="Go to previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
      );
    }

    return (
      <PaginationPrevious
        onClick={() => onPageChange(currentPage - 1)}
        tabIndex={currentPage === 1 ? -1 : 0}
        className={
          currentPage === 1
            ? "pointer-events-none opacity-50"
            : "cursor-pointer"
        }
      />
    );
  };

  // Custom Next button that's just an arrow on mobile
  const CustomNext = () => {
    if (isMobile) {
      return (
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`flex h-9 w-9 items-center justify-center rounded-md border ${
            currentPage === totalPages
              ? "pointer-events-none opacity-50"
              : "hover:bg-muted cursor-pointer"
          }`}
          aria-label="Go to next page"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      );
    }

    return (
      <PaginationNext
        onClick={() => onPageChange(currentPage + 1)}
        tabIndex={currentPage === totalPages ? -1 : 0}
        className={
          currentPage === totalPages
            ? "pointer-events-none opacity-50"
            : "cursor-pointer"
        }
      />
    );
  };

  return (
    <Pagination>
      <PaginationContent className="flex items-center justify-center gap-1">
        <PaginationItem>
          <CustomPrev />
        </PaginationItem>

        {renderPageNumbers()}

        <PaginationItem>
          <CustomNext />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}

// Posts per page
const POSTS_PER_PAGE = 4;

/**
 * Blog layout component that provides the common structure for both the blog index and loading state
 */
interface BlogLayoutProps {
  children: ReactNode;
}

function BlogLayout({ children }: BlogLayoutProps) {
  return (
    <div className="font-handwriting flex justify-center">
      <div className="mx-auto flex w-full max-w-[1800px] px-4 pt-6">
        <div className="min-w-0 flex-1">
          <div className="mx-auto max-w-5xl">
            <div className="mb-8 text-center">
              <h1 className="font-handwriting mb-4 text-center text-4xl font-bold">
                Blog
              </h1>
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

interface BlogPageProps {
  /**
   * Blog posts metadata
   */
  posts: BlogMeta[];
}

export function BlogPage({ posts }: BlogPageProps) {
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
      <BlogLayout>
        <div className="mb-10 min-h-[700px]">
          {posts.length === 0 ? (
            <div className="py-12 text-center">
              <h2 className="text-foreground text-xl font-medium">
                No posts found
              </h2>
              <p className="text-foreground mt-2">
                Check back soon for new content!
              </p>
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
                  <div className="bg-background border-border flex h-[320px] flex-col overflow-hidden rounded-lg border shadow-sm transition-all duration-200 hover:shadow-lg">
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
              {Array.from({
                length: Math.max(0, POSTS_PER_PAGE - currentPosts.length),
              }).map((_, index) => (
                <div
                  key={`spacer-${index}`}
                  className="invisible h-[320px] md:h-[320px]"
                />
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
