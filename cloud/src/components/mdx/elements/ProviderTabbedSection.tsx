import { useEffect, useRef, useState } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/mirascope-ui/ui/tabs";
import { ProductLogo } from "@/src/components/core/branding";
import { cn } from "@/src/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";
import {
  useProvider,
  type Provider,
  providers,
  providerDefaults,
} from "@/src/components/core/providers/ProviderContext";

/**
 * A tabbed section component that creates tabs for each provider
 * and integrates with the provider context for selection state
 */
export function ProviderTabbedSection({
  children,
  className = "",
  showLogo = false,
  customHeader = null,
}: {
  children: React.ReactNode;
  className?: string;
  showLogo?: boolean;
  customHeader?: React.ReactNode;
}) {
  const { provider, setProvider } = useProvider();
  const [activeProvider, setActiveProvider] = useState<Provider>(provider);
  const tabsListRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  // When the provider context changes, update the active provider
  useEffect(() => {
    setActiveProvider(provider);

    // Scroll the selected tab into view
    if (tabsListRef.current) {
      const selectedTab = tabsListRef.current.querySelector(`[data-state="active"]`);
      if (selectedTab) {
        const tabsList = tabsListRef.current;
        const tabsListRect = tabsList.getBoundingClientRect();
        const selectedTabRect = selectedTab.getBoundingClientRect();

        // Calculate the distance to scroll
        const scrollLeft =
          selectedTabRect.left -
          tabsListRect.left +
          tabsList.scrollLeft -
          tabsListRect.width / 2 +
          selectedTabRect.width / 2;

        tabsList.scrollTo({
          left: scrollLeft,
          behavior: "smooth",
        });

        // Update scroll indicators after scrolling
        setTimeout(checkScrollability, 300);
      }
    }
  }, [provider]);

  // Function to check scroll availability
  const checkScrollability = () => {
    if (tabsListRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = tabsListRef.current;
      // Can scroll left if we're not at or very close to the beginning (using 5px threshold)
      setCanScrollLeft(scrollLeft > 5);
      // Can scroll right if there's more content to show
      setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 1); // -1 for rounding errors
    }
  };

  // Handle tab change
  const handleProviderChange = (value: string) => {
    const newProvider = value as Provider;
    setProvider(newProvider);
  };

  // Scroll left/right handlers
  const scrollLeft = () => {
    if (tabsListRef.current) {
      const scrollAmount = tabsListRef.current.clientWidth / 2;
      tabsListRef.current.scrollBy({ left: -scrollAmount, behavior: "smooth" });
    }
  };

  const scrollRight = () => {
    if (tabsListRef.current) {
      const scrollAmount = tabsListRef.current.clientWidth / 2;
      tabsListRef.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  // Setup scroll event listeners
  useEffect(() => {
    const tabsList = tabsListRef.current;
    if (tabsList) {
      // Initial check
      checkScrollability();

      // Set up listeners
      tabsList.addEventListener("scroll", checkScrollability);
      window.addEventListener("resize", checkScrollability);

      return () => {
        tabsList.removeEventListener("scroll", checkScrollability);
        window.removeEventListener("resize", checkScrollability);
      };
    }
  }, []);

  return (
    <div
      className={cn(
        "bg-card overflow-hidden rounded-md border-1 px-2 pt-2 pb-0 shadow-md",
        className
      )}
    >
      {customHeader ? (
        customHeader
      ) : showLogo ? (
        <div className="flex items-center px-1 pb-2">
          <ProductLogo size="micro" withText={true} />
        </div>
      ) : null}

      <Tabs value={activeProvider} onValueChange={handleProviderChange} className="mb-2 w-full">
        <div className="relative mb-0">
          {/* Left scroll button - always rendered but conditionally visible */}
          <button
            onClick={canScrollLeft ? scrollLeft : undefined}
            className={`bg-background/60 absolute top-1/2 left-0 z-10 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full shadow-md backdrop-blur-sm transition-opacity duration-200 ${canScrollLeft ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"}`}
            aria-label="Scroll tabs left"
            aria-hidden={!canScrollLeft}
          >
            <ChevronLeft className="h-3 w-3" />
          </button>

          <div
            ref={tabsListRef}
            className="hide-scrollbar overflow-x-auto pb-0"
            onScroll={checkScrollability}
          >
            <TabsList className="inline-flex h-auto flex-nowrap gap-x-2 bg-transparent p-0">
              {providers.map((p) => (
                <TabsTrigger key={p} value={p} className="whitespace-nowrap">
                  {providerDefaults[p].displayName}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          {/* Right scroll button - always rendered but conditionally visible */}
          <button
            onClick={canScrollRight ? scrollRight : undefined}
            className={`bg-background/60 absolute top-1/2 right-0 z-10 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full shadow-md backdrop-blur-sm transition-opacity duration-200 ${canScrollRight ? "pointer-events-auto opacity-100" : "pointer-events-none opacity-0"}`}
            aria-label="Scroll tabs right"
            aria-hidden={!canScrollRight}
          >
            <ChevronRight className="h-3 w-3" />
          </button>
        </div>
      </Tabs>
      {children}
    </div>
  );
}
