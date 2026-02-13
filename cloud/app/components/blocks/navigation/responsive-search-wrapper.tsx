import { Search as SearchIcon, X } from "lucide-react";
import { useState } from "react";

import { useIsWatercolorPage } from "@/app/components/blocks/theme-provider";
import { useIsMobile } from "@/app/hooks/is-mobile";

import { SearchBar } from "./search-bar";
// import SearchBar from "@/app/components/blocks/navigation/search-bar";
import { SEARCH_BAR_STYLES } from "./styles";

/**
 * Props for search wrappers
 */
interface SearchWrapperProps {
  /**
   * Called when search open state changes
   */
  onOpenChange: (isOpen: boolean) => void;
}

/**
 * Mobile-specific search UI with overlay
 */
function MobileSearchWrapper({ onOpenChange }: SearchWrapperProps) {
  // Manage internal state for mobile search
  const [isOpen, setIsOpen] = useState(false);
  const isWatercolorPage = useIsWatercolorPage();

  // Open mobile search handler
  const handleOpenSearch = () => {
    setIsOpen(true);
    onOpenChange(true);
  };

  // Close mobile search handler
  const handleCloseSearch = () => {
    setIsOpen(false);
    onOpenChange(false);
  };

  // Handle search state changes from SearchBar
  const handleSearchOpenChange = (open: boolean) => {
    if (!open) {
      // Only handle close events from SearchBar
      handleCloseSearch();
    }
  };

  if (!isOpen) {
    return (
      <button
        className={`hover:cursor-pointer ${SEARCH_BAR_STYLES.mobileSearchButton(
          isWatercolorPage,
        )}`}
        style={SEARCH_BAR_STYLES.getInputContainerStyles(isWatercolorPage)}
        onClick={handleOpenSearch}
        aria-label="Open search"
      >
        <SearchIcon size={16} />
      </button>
    );
  }

  return (
    <>
      {/* Mobile search overlay - full screen with click-outside behavior */}
      <div
        className={SEARCH_BAR_STYLES.mobileOverlay(isOpen)}
        onClick={handleCloseSearch} // Close when clicking the background overlay
      >
        {/* Search container - prevent clicks from bubbling up to the overlay */}
        <div
          className={SEARCH_BAR_STYLES.mobileSearchContainer}
          onClick={(e) => e.stopPropagation()} // Prevent clicks from closing the search
        >
          {/* SearchBar in the overlay */}
          <div className="relative grow">
            <SearchBar
              onOpenChange={handleSearchOpenChange}
              initialIsOpen={true} // Force it to start in open state
              onResultSelect={handleCloseSearch} // Close the overlay when a result is selected
            />

            {/* Close button positioned on the right side */}
            <button
              className={SEARCH_BAR_STYLES.closeButton(isWatercolorPage)}
              onClick={handleCloseSearch}
              aria-label="Close search"
            >
              <X size={20} />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

/**
 * Responsive wrapper that renders either mobile or desktop search UI
 * based on screen size
 */
export default function ResponsiveSearchWrapper({
  onOpenChange,
}: SearchWrapperProps) {
  // Use the mobile detection hook
  const isMobile = useIsMobile();

  // Choose the appropriate UI based on screen size
  if (isMobile) {
    return <MobileSearchWrapper onOpenChange={onOpenChange} />;
  }

  // Desktop UI - render the SearchBar normally
  return (
    <SearchBar
      onOpenChange={onOpenChange}
      onResultSelect={() => onOpenChange(false)}
    />
  );
}
