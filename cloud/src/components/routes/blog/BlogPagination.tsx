import { useIsMobile } from "@/src/components/routes/root/hooks/useIsMobile";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/src/components/ui/pagination";
import { ChevronLeft, ChevronRight } from "lucide-react";

export interface BlogPaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function BlogPagination({
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
