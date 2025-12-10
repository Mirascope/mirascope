// Import directly to avoid circular dependency through barrel exports
import { PageMeta } from "@/src/components/core/meta/PageMeta";
import { useSunsetTime } from "@/src/lib/hooks/useSunsetTime";
import { useGradientFadeOnScroll } from "@/src/lib/hooks/useGradientFadeOnScroll";
import { useRef, useState, useEffect } from "react";
import { ProviderContextProvider } from "@/src/components/core/providers/ProviderContext";
import { HeroBlock } from "./HeroBlock";
import { MirascopeBlock } from "./MirascopeBlock";
import { LilypadBlock } from "./LilypadBlock";

export function LandingPage() {
  useSunsetTime();
  useGradientFadeOnScroll({ fadeStartDistance: 100, fadeEndDistance: 10 });

  const heroSectionRef = useRef<HTMLDivElement>(null);
  const mirascopeSectionRef = useRef<HTMLDivElement>(null);
  const lilypadSectionRef = useRef<HTMLDivElement>(null);

  const [showScrollButton, setShowScrollButton] = useState(true);

  // Function to scroll to hero section (top of page)
  const scrollToHeroSection = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Update URL hash without causing a jump
    window.history.pushState(null, "", "#hero");
  };

  // Function to scroll to mirascope section with offset for better positioning
  const scrollToMirascopeSection = () => {
    if (mirascopeSectionRef.current) {
      const yOffset = -window.innerHeight * -0.02;
      const element = mirascopeSectionRef.current;
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

      window.scrollTo({ top: y, behavior: "smooth" });

      // Update URL hash without causing a jump
      window.history.pushState(null, "", "#mirascope");
    }
  };

  // Function to scroll to lilypad section with offset for better positioning
  const scrollToLilypadSection = () => {
    if (lilypadSectionRef.current) {
      const yOffset = -window.innerHeight * 0.02;
      const element = lilypadSectionRef.current;
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;

      window.scrollTo({ top: y, behavior: "smooth" });

      // Update URL hash without causing a jump
      window.history.pushState(null, "", "#lilypad");
    }
  };

  // Function to hide button when scrolled past the first section
  // Handle hash navigation on page load
  useEffect(() => {
    // Check if a hash is present in the URL
    const hash = window.location.hash;
    if (hash) {
      // Remove the '#' character
      const targetId = hash.substring(1);

      // Delay to ensure everything is properly rendered
      setTimeout(() => {
        if (targetId === "mirascope") {
          scrollToMirascopeSection();
        } else if (targetId === "lilypad") {
          scrollToLilypadSection();
        } else if (targetId === "hero") {
          scrollToHeroSection();
        }
      }, 300);
    }

    // Handle hash changes after page load
    const handleHashChange = () => {
      const currentHash = window.location.hash.substring(1);

      if (currentHash === "mirascope") {
        scrollToMirascopeSection();
      } else if (currentHash === "lilypad") {
        scrollToLilypadSection();
      } else if (currentHash === "hero") {
        scrollToHeroSection();
      }
    };

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  // Track scroll position and update URL hash accordingly
  useEffect(() => {
    // Debounce timeout to avoid excessive hash updates
    let scrollTimeout: number | null = null;

    const handleScroll = () => {
      if (heroSectionRef.current) {
        const heroHeight = heroSectionRef.current.offsetHeight;
        const scrollPosition = window.scrollY;

        // Hide button when scrolled past 40% of the hero section height
        setShowScrollButton(scrollPosition < heroHeight * 0.4);
      }

      // Debounce the hash update to avoid excessive updates during scrolling
      if (scrollTimeout) {
        clearTimeout(scrollTimeout);
      }

      scrollTimeout = window.setTimeout(() => {
        const mirascopePosition = mirascopeSectionRef.current?.getBoundingClientRect().top || 0;
        const lilypadPosition = lilypadSectionRef.current?.getBoundingClientRect().top || 0;

        // Determine which section is currently most visible
        if (lilypadPosition < window.innerHeight / 2 && lilypadSectionRef.current) {
          // We're in the lilypad section
          if (window.location.hash !== "#lilypad") {
            window.history.pushState(null, "", "#lilypad");
          }
        } else if (mirascopePosition < window.innerHeight / 2 && mirascopeSectionRef.current) {
          // We're in the mirascope section
          if (window.location.hash !== "#mirascope") {
            window.history.pushState(null, "", "#mirascope");
          }
        } else {
          // We're in the hero section or above all sections
          // Use a dedicated hash for hero section instead of removing hash completely
          // This prevents TanStack Router from treating it as a new navigation
          if (window.location.hash !== "#hero") {
            window.history.pushState(null, "", "#hero");
          }
        }
      }, 16); // 16ms debounce
    };

    window.addEventListener("scroll", handleScroll);
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (scrollTimeout) clearTimeout(scrollTimeout);
    };
  }, []);

  return (
    <>
      <PageMeta title="Home" description="The AI Engineer's Developer Stack" />
      <ProviderContextProvider>
        <div className="flex w-full flex-col">
          {/* Hero section */}
          <div data-gradient-fade={true} ref={heroSectionRef}>
            <HeroBlock
              onScrollDown={scrollToMirascopeSection}
              showScrollButton={showScrollButton}
            />
          </div>

          {/* Mirascope section */}
          <div data-gradient-fade={true} ref={mirascopeSectionRef} className="mb-24">
            <MirascopeBlock onScrollDown={scrollToLilypadSection} />
          </div>

          {/* Lilypad section */}
          <div data-gradient-fade={true} ref={lilypadSectionRef} className="mt-24">
            <LilypadBlock onScrollToTop={scrollToHeroSection} />
          </div>
        </div>
      </ProviderContextProvider>
    </>
  );
}
