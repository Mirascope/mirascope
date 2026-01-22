import React, { useState, useRef, useEffect } from "react";
import DOMPurify from "dompurify";
import { Search as SearchIcon } from "lucide-react";
import { Link } from "@tanstack/react-router";
import {
  getSearchService,
  type SearchResultItem,
} from "@/app/lib/search/service";
import { useIsLandingPage } from "@/app/components/blocks/theme-provider";
import { SEARCH_BAR_STYLES, ANIMATION_TIMING } from "./styles";
import { useIsMobile } from "@/app/hooks/is-mobile";
import { isDevelopment } from "@/app/lib/site";

/**
 * Sanitizes search excerpt HTML to prevent XSS attacks.
 * Only allows <mark> tags for search term highlighting.
 */
function sanitizeExcerpt(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ["mark"],
    ALLOWED_ATTR: [],
  });
}

// Component for an individual search result
interface SearchResultProps {
  result: SearchResultItem;
  onSelect: () => void;
  isSelected?: boolean;
  index: number;
  onHover: (index: number) => void;
}

function SearchResult({
  result,
  onSelect,
  isSelected = false,
  index,
  onHover,
}: SearchResultProps) {
  // Get development mode from environment

  // Get description and excerpt separately
  const description = result.meta?.description;
  const excerpt = result.excerpt;

  return (
    <Link
      to={result.url}
      onClick={onSelect}
      onMouseEnter={() => onHover(index)}
      onMouseMove={() => onHover(index)}
      className={SEARCH_BAR_STYLES.result(isSelected)}
    >
      <div className="min-w-0 flex-1">
        <div className="mb-2 flex items-center justify-between">
          <h4 className="text-accent-foreground truncate text-base font-medium">
            {result.title || "Untitled"}
          </h4>
          <div className="flex items-center gap-2">
            {/* Section badge */}
            <span className="bg-muted text-muted-foreground max-w-[150px] truncate rounded px-1.5 py-0.5 text-[10px]">
              {result.section}
            </span>

            {/* Score indicator in development mode */}
            {isDevelopment() && result.score !== undefined && (
              <span className="text-muted-foreground text-[10px]">
                {result.score.toFixed(2)}
              </span>
            )}
          </div>
        </div>

        {/* Description - shown if available */}
        {description && (
          <p className="text-muted-foreground search-description mb-1.5 line-clamp-2 text-sm">
            {description}
          </p>
        )}

        {/* Excerpt - always shown, italicized */}
        <p
          className="text-muted-foreground search-excerpt line-clamp-2 text-xs italic"
          dangerouslySetInnerHTML={{ __html: sanitizeExcerpt(excerpt) }}
        />
      </div>
    </Link>
  );
}

// Maximum number of search results to display
const MAX_DISPLAYED_RESULTS = 20;

// Duration to block focus events after result selection to prevent search from reopening
const FOCUS_BLOCK_DURATION = 200;

// Component for a list of search results
interface SearchResultListProps {
  results: SearchResultItem[];
  onResultSelect: () => void;
  selectedIndex: number;
  onHover: (index: number) => void;
}

function SearchResultList({
  results,
  onResultSelect,
  selectedIndex,
  onHover,
}: SearchResultListProps) {
  // Only display up to MAX_DISPLAYED_RESULTS
  const displayedResults = results.slice(0, MAX_DISPLAYED_RESULTS);

  return (
    <div>
      {displayedResults.map((result, idx) => (
        <SearchResult
          key={`${result.url}-${idx}`}
          result={result}
          onSelect={onResultSelect}
          isSelected={idx === selectedIndex}
          index={idx}
          onHover={onHover}
        />
      ))}
      {results.length > MAX_DISPLAYED_RESULTS && (
        <div className="text-muted-foreground border-border/40 border-t px-4 py-2 text-center text-xs">
          Showing top {MAX_DISPLAYED_RESULTS} of {results.length} results
        </div>
      )}
    </div>
  );
}

// Component for the search input
interface SearchInputProps {
  query: string;
  onChange: (value: string) => void;
  onFocus: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
  isOpen: boolean;
  isMobile?: boolean;
}

function SearchInput({
  query,
  onChange,
  onFocus,
  inputRef,
  isOpen,
  isMobile = false,
}: SearchInputProps) {
  const isLandingPage = useIsLandingPage();
  return (
    <div
      className={SEARCH_BAR_STYLES.inputContainer(isLandingPage, isMobile)}
      data-testid="search-input"
      style={SEARCH_BAR_STYLES.getInputContainerStyles(isLandingPage)}
      onClick={onFocus}
    >
      <SearchIcon size={16} className={SEARCH_BAR_STYLES.icon(isOpen)} />
      <input
        ref={inputRef}
        readOnly={!isOpen}
        type="text"
        placeholder="Search..."
        className={SEARCH_BAR_STYLES.input(isOpen, isLandingPage, isMobile)}
        value={query}
        onChange={(e) => onChange(e.target.value)}
        onFocus={onFocus}
        autoFocus={isMobile && isOpen} // Auto-focus in mobile mode
      />
      <kbd className={SEARCH_BAR_STYLES.kbd(isLandingPage, isOpen)}>
        <span className="text-xs">⌘</span>K
      </kbd>
    </div>
  );
}

// Component for the search results container
interface SearchResultsContainerProps {
  isOpen: boolean;
  isLoading: boolean;
  isSearching: boolean;
  isPagefindLoaded: boolean;
  error: string;
  query: string;
  results: SearchResultItem[];
  resultsRef: React.RefObject<HTMLDivElement | null>;
  onResultSelect: () => void;
  selectedIndex: number;
  setSelectedIndex: (index: number) => void;
  isMobile?: boolean;
}

function SearchResultsContainer({
  isOpen,
  isLoading,
  isSearching,
  isPagefindLoaded,
  error,
  query,
  results,
  resultsRef,
  onResultSelect,
  selectedIndex,
  setSelectedIndex,
  isMobile = false,
}: SearchResultsContainerProps) {
  const isLandingPage = useIsLandingPage();
  return (
    <div
      className={SEARCH_BAR_STYLES.resultsContainer(
        isLandingPage,
        isMobile,
        isOpen,
      )}
      style={SEARCH_BAR_STYLES.getResultsContainerStyles(isLandingPage)}
      ref={resultsRef}
    >
      {renderSearchContent()}
      <SearchFooter />
    </div>
  );

  function renderSearchContent() {
    if (isLoading && !isPagefindLoaded) {
      return (
        <div className="text-muted-foreground p-6 text-center">
          Loading search engine...
        </div>
      );
    }

    if (isLoading || isSearching) {
      return (
        <div className="flex justify-center p-4">
          <div className={SEARCH_BAR_STYLES.loadingIndicator}></div>
          <span className="sr-only">Loading results...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-muted-foreground p-4 text-center">
          <p className="mb-2">Search index not available</p>
          <p className="text-xs">
            Run{" "}
            <code className="bg-muted rounded px-1 py-0.5">bun run build</code>{" "}
            to generate the search index
          </p>
        </div>
      );
    }

    // Check if we have any results to show
    const hasResults = results.length > 0;

    if (hasResults) {
      return (
        <div className="max-h-[calc(100vh-200px)] overflow-y-auto">
          <SearchResultList
            results={results}
            onResultSelect={onResultSelect}
            selectedIndex={selectedIndex}
            onHover={setSelectedIndex}
          />
        </div>
      );
    }

    // Only show "No results" if we're not in a loading or searching state
    // and there's actually no results to show
    if (query.trim() && !isLoading && !isSearching && !hasResults) {
      return (
        <div className="text-muted-foreground p-4 text-center">
          No results found for "{query}"
        </div>
      );
    }

    return (
      <div className="text-muted-foreground font-handwriting p-4 text-center">
        Type to search
      </div>
    );
  }
}

// Component for the keyboard shortcut footer
function SearchFooter() {
  const isMobile = useIsMobile();

  // Hide footer completely on mobile
  if (isMobile) {
    return null;
  }

  return (
    <div className={SEARCH_BAR_STYLES.footer}>
      <div className="flex items-center gap-2 px-2">
        <kbd className="border-border rounded border px-1.5 py-0.5 text-[12px]">
          <span className="pr-1 text-xs">⌘</span>
          <span>K</span>
        </kbd>
        <span>to search</span>
      </div>
      <div className="flex items-center gap-2 px-2">
        <kbd className="border-border rounded border px-1.5 py-0.5 text-[10px]">
          Esc
        </kbd>
        <span>to close</span>
      </div>
    </div>
  );
}

interface SearchBarProps {
  /**
   * Called when search open state changes
   */
  onOpenChange?: (isOpen: boolean) => void;

  /**
   * Initial open state (useful for mobile overlay)
   */
  initialIsOpen?: boolean;

  /**
   * Called when a search result is selected
   * Useful to close the overlay
   */
  onResultSelect?: () => void;
}

export function SearchBar({
  onOpenChange,
  initialIsOpen = false,
  onResultSelect,
}: SearchBarProps = {}) {
  const [isOpen, setIsOpen] = useState(initialIsOpen);
  const [isClosingFromResult, setIsClosingFromResult] = useState(false);

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const [isPagefindLoaded, setIsPagefindLoaded] = useState(false);
  const isMobile = useIsMobile();

  // Get the search service
  const searchService = getSearchService();

  // Focus input when search is opened
  useEffect(() => {
    if ((isOpen || initialIsOpen || isMobile) && inputRef.current) {
      // Use a short timeout to ensure the DOM is ready and focus works reliably
      setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
    }

    // For mobile mode, don't call onOpenChange from within this effect
    // to avoid circular callback chain
    if (isMobile) {
      return;
    }

    // Only for desktop: Use a slight delay to toggle visibility
    if (isOpen) {
      // Hide navigation immediately
      if (onOpenChange) onOpenChange(true);
    } else {
      // Show navigation after search closes with a delay that matches our animation
      const timer = setTimeout(() => {
        if (onOpenChange) onOpenChange(false);
      }, ANIMATION_TIMING.getTotalDuration()); // Use centralized timing
      return () => clearTimeout(timer);
    }
  }, [isOpen, initialIsOpen, onOpenChange, isMobile]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: globalThis.KeyboardEvent) => {
      // Close on escape key
      if (e.key === "Escape") {
        setIsOpen(false);
        // Explicitly call onOpenChange for mobile mode to close the overlay
        if (isMobile && onOpenChange) {
          onOpenChange(false);
        }
      }

      // Open on Cmd+K or Ctrl+K
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setIsOpen(true);
      }

      // Only handle arrow keys when search is open and we have results
      if (isOpen && results.length > 0) {
        // Navigate down with down arrow
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setSelectedIndex((prevIndex) =>
            prevIndex < Math.min(results.length - 1, MAX_DISPLAYED_RESULTS - 1)
              ? prevIndex + 1
              : prevIndex,
          );
        }

        // Navigate up with up arrow
        if (e.key === "ArrowUp") {
          e.preventDefault();
          setSelectedIndex((prevIndex) =>
            prevIndex > 0 ? prevIndex - 1 : prevIndex,
          );
        }

        // Select item with Enter key
        if (
          e.key === "Enter" &&
          selectedIndex >= 0 &&
          selectedIndex < results.length
        ) {
          e.preventDefault();
          // Let the result selection be handled by the Link component
          // by programmatically clicking the selected result item
          const resultElements = resultsRef.current?.querySelectorAll("a");
          if (resultElements && resultElements[selectedIndex]) {
            resultElements[selectedIndex].click();
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, results, selectedIndex, onOpenChange, isMobile]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Initialize search service when the search is opened for the first time
  useEffect(() => {
    if (isOpen && !isPagefindLoaded) {
      void initializeSearch();
    }
  }, [isOpen, isPagefindLoaded]);

  // Perform search when query changes
  useEffect(() => {
    if (!query.trim() || !isPagefindLoaded) {
      setResults([]);
      return;
    }

    // Set searching state immediately when query changes
    setIsSearching(true);
    setIsLoading(true);

    const performSearch = async () => {
      try {
        // Use the search service to perform the search
        const response = await searchService.search(query);

        // If null, a new search will be started soon, so maintain loading state
        if (response === null) {
          return;
        }

        // Update state with the results
        setResults(response.items);
        setError("");
        setIsLoading(false);
        setIsSearching(false);
      } catch (error) {
        console.error("Search error:", error);
        setError(error instanceof Error ? error.message : "Failed to search");
        setResults([]);
        setIsLoading(false);
        setIsSearching(false);
      }
    };

    void performSearch();

    return () => {
      // No need to clean up timers as search service handles debouncing internally
    };
  }, [query, isPagefindLoaded, searchService]);

  // Handle result selection - closes the search interface
  const handleResultSelect = () => {
    // Set flag to prevent focus events from reopening search during navigation
    setIsClosingFromResult(true);

    setIsOpen(false);
    setQuery("");

    // Call the onResultSelect prop to close the overlay/modal
    if (onResultSelect) {
      onResultSelect();
    }

    // Clear the flag after navigation has had time to complete
    setTimeout(() => {
      setIsClosingFromResult(false);
    }, FOCUS_BLOCK_DURATION);
  };

  // Initialize the search service
  const initializeSearch = async () => {
    try {
      setIsLoading(true);

      if (isDevelopment()) {
        console.log("🔍 [SearchBar] Initializing search service...");
      }

      await searchService.init();
      setIsPagefindLoaded(true);
      setError("");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "An error occurred";
      if (isDevelopment()) {
        console.error("🔍 [SearchBar] Error initializing search:", error);
      }
      setError(errorMessage);
      setIsPagefindLoaded(false);
    } finally {
      setIsLoading(false);
    }
  };

  // When new search results arrive, reset the selected index
  useEffect(() => {
    setSelectedIndex(0);
  }, [results]);

  // For mobile mode, use a simpler container without animations
  const containerClassName = isMobile
    ? "relative flex items-center w-full" // Full width, no transitions
    : SEARCH_BAR_STYLES.container(isOpen);

  return (
    <div className={containerClassName} ref={searchContainerRef}>
      <SearchInput
        query={query}
        onChange={setQuery}
        onFocus={() => {
          // Prevent reopening search if we just closed it due to result selection
          if (isClosingFromResult) {
            return;
          }
          setIsOpen(true);
        }}
        inputRef={inputRef}
        isOpen={isOpen || isMobile} // Always show as open in mobile mode
        isMobile={isMobile}
      />

      <SearchResultsContainer
        isOpen={isOpen || (isMobile && query.trim().length > 0)} // Always show in mobile with query
        isLoading={isLoading}
        isSearching={isSearching}
        isPagefindLoaded={isPagefindLoaded}
        error={error}
        query={query}
        results={results}
        resultsRef={resultsRef}
        onResultSelect={handleResultSelect}
        selectedIndex={selectedIndex}
        setSelectedIndex={setSelectedIndex}
        isMobile={isMobile}
      />
    </div>
  );
}
