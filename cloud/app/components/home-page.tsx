import { useEffect, useRef, useState } from "react";
import { cn } from "@/app/lib/utils";
import { useSunsetTime } from "@/app/hooks/sunset-time";
import { useGradientFadeOnScroll } from "@/app/hooks/gradient-fade-scroll";
import { BookOpen, ChevronDown, ChevronUp, Rocket, Users } from "lucide-react";
import { ButtonLink } from "@/app/components/ui/button-link";
import homeStyles from "@/app/components/home-page.module.css";
import { ResponsiveTextBlock } from "@/app/components/blocks/responsive-text-block";

// Shared styling constants for logo and hero components
// This ensures we maintain consistency and makes future updates easier
const styleSystem = {
  // Base dimensions for different components
  logoFontSize: "clamp(1.75rem, 4.5vw, 3.5rem)", // Smaller than hero text
  heroFontSize: "clamp(2.5rem, 8vw, 6rem)", // Larger than logo text
  lineHeightMultiplier: 0.9,

  // Spacing modifiers
  paddingInlineMultiplier: 0.75,
  paddingBlockMultiplier: 0.375,
  logoImageSpacingMultiplier: 0.375,
  logoToHeroSpacingMultiplier: 1,

  // Fine-tuning adjustment for vertical centering (positive = move up)
  centeringAdjustment: "0rem",
};

// Derived styles for logo component
const logoStyles = {
  // Base dimensions from style system
  fontSize: styleSystem.logoFontSize,
  lineHeightMultiplier: styleSystem.lineHeightMultiplier,

  // Derived measurements
  get lineHeight() {
    return `calc(${this.fontSize} * ${this.lineHeightMultiplier})`;
  },

  // Calculated spacing values
  get paddingInline() {
    return `calc(${this.lineHeight} * ${styleSystem.paddingInlineMultiplier})`;
  },
  get paddingBlock() {
    return `calc(${this.lineHeight} * ${styleSystem.paddingBlockMultiplier})`;
  },
  get totalPaddingBlock() {
    return `calc(${this.lineHeight} * ${styleSystem.paddingBlockMultiplier} * 2)`;
  },
  get logoImageSpacing() {
    return `calc(${this.lineHeight} * ${styleSystem.logoImageSpacingMultiplier})`;
  },
  get logoToHeroSpacing() {
    return `calc(${this.lineHeight} * ${styleSystem.logoToHeroSpacingMultiplier})`;
  },

  // Centering calculation - uses values from both logo and hero
  get centeringOffset() {
    // Half of (logo height + total vertical padding + spacing to hero)
    // Plus an additional adjustment for fine-tuning
    return `calc(((${this.lineHeight} + ${this.totalPaddingBlock} + 3 * ${this.logoToHeroSpacing}) / 2) + ${styleSystem.centeringAdjustment})`;
  },
};

// Logo banner component with responsive sizing
const LogoBanner = () => {
  return (
    <div
      className="relative"
      style={{
        // Use the shared styles for consistent dimensions
        paddingInline: logoStyles.paddingInline,
        paddingBlock: logoStyles.paddingBlock,
      }}
    >
      {/* Torn paper background effect */}
      <div className="absolute inset-0 bg-white torn-paper-effect"></div>

      {/* Logo content */}
      <div className="relative z-10">
        <div className="flex flex-row items-center justify-center">
          {/* Logo image */}
          <div style={{ marginRight: logoStyles.logoImageSpacing }}>
            <img
              src="/assets/branding/mirascope-logo.svg"
              alt="Mirascope Frog Logo"
              style={{
                height: logoStyles.fontSize,
                width: "auto",
              }}
            />
          </div>

          {/* Logo text */}
          <h1
            style={{
              fontSize: logoStyles.fontSize,
              marginBottom: 0,
              lineHeight: logoStyles.lineHeightMultiplier,
            }}
            className="font-handwriting text-mirascope-purple"
          >
            Mirascope
          </h1>
        </div>
      </div>
    </div>
  );
};

// Hero block component with logo and text
export interface HeroBlockProps {
  onScrollDown: () => void;
  showScrollButton: boolean;
}

function HeroBlock({ onScrollDown, showScrollButton }: HeroBlockProps) {
  return (
    <div
      className="relative h-screen"
      style={{ marginTop: "calc(var(--header-height-base) * -1)" }}
    >
      {/* Container that centers the entire block in the viewport */}
      <div className="absolute inset-0 flex flex-col items-center justify-center px-4">
        {/* Content wrapper with computed negative margin to center the hero text */}
        <div
          className="flex flex-col items-center"
          style={{
            /* Use the shared calculated offset to center the hero text */
            marginTop: `calc(${logoStyles.centeringOffset} * -1)`,
          }}
        >
          <div
            style={{
              marginBottom: logoStyles.logoToHeroSpacing,
            }}
          >
            <LogoBanner />
          </div>

          <div className="text-center">
            <ResponsiveTextBlock
              lines={["The AI Engineer's", "Developer Stack"]}
              fontSize={styleSystem.heroFontSize}
              className="flex flex-col font-medium tracking-tight text-white"
              lineClassName="font-handwriting"
              textShadow={true}
            />
          </div>
        </div>
        <div className="mt-8 flex w-full max-w-3xl flex-col items-center justify-center gap-4 sm:flex-row">
          <ButtonLink
            href="/docs/mirascope/v2"
            variant="outline"
            size="lg"
            className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] border-0 bg-white text-center font-handwriting font-bold text-black hover:bg-white/90 hover:text-black sm:w-auto"
          >
            <Rocket className="size-5" aria-hidden="true" />
            Mirascope v2 Alpha
          </ButtonLink>
          <ButtonLink
            href="/discord-invite"
            variant="default"
            size="lg"
            className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] bg-[#5865F2] text-center font-handwriting font-bold text-white hover:bg-[#5865F2]/90 sm:w-auto"
          >
            Join our
            <img
              src="/assets/branding/Discord-Logo-White.svg"
              alt="Discord"
              className="h-3.5 w-auto"
            />
          </ButtonLink>
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className={cn(
          "fixed right-0 bottom-16 left-0 z-10 flex justify-center transition-opacity duration-300",
          showScrollButton ? "opacity-100" : "pointer-events-none opacity-0",
        )}
      >
        <div className="landing-page-box-shadow landing-page-box-shadow-hover relative h-12 w-12 overflow-hidden rounded-full">
          <button
            onClick={onScrollDown}
            className="bg-primary/80 hover:bg-primary absolute inset-0 flex items-center justify-center border-0 transition-all"
            aria-label="Scroll to learn more"
          >
            <ChevronDown className="h-6 w-6 text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
export interface MirascopeBlockProps {
  onScrollToTop?: () => void;
}

export const MirascopeBlock = ({ onScrollToTop }: MirascopeBlockProps) => {
  // todo(seb): bring back code example
  //   const codeExample = `from mirascope import llm
  // from pydantic import BaseModel

  // class Book(BaseModel):
  //     title: str
  //     author: str

  // # [!code highlight:6]
  // @llm.call(
  //     provider="$PROVIDER",
  //     model="$MODEL",
  //     response_model=Book,
  // )
  // def extract_book(text: str) -> str:
  //     return f"Extract the book: {text}"

  // text = "The Name of the Wind by Patrick Rothfuss"
  // book: Book = extract_book(text) # [!code highlight]`;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-16">
      {/* todo(seb): Add responsive text block */}
      {/* <ResponsiveTextBlock
        lines={["LLM abstractions that", "aren't obstructions"]}
        element="h2"
        fontSize="clamp(1.5rem, 5vw, 3rem)"
        className="text-shadow-medium mb-6 text-center text-white"
        lineClassName="font-bold"
        lineSpacing="mb-2"
      /> */}
      <div className="bg-background/60 mb-2 w-full max-w-3xl rounded-md">
        {/* todo(seb): Add provider tabbed section */}
        {/* <ProviderTabbedSection
          customHeader={
            <div className="flex items-center px-1 pb-2">
              <MirascopeLogo size="micro" withText={true} />
            </div>
          }
        >
          <ProviderCodeWrapper className="textured-bg" code={codeExample} language="python" />
        </ProviderTabbedSection> */}
      </div>

      <div className="mt-2 flex w-full max-w-3xl flex-col items-center justify-center gap-4 sm:flex-row">
        <ButtonLink
          href="/docs/mirascope"
          variant="default"
          size="default"
          className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] px-6 py-4 text-center font-handwriting font-medium sm:w-auto"
        >
          <BookOpen className="size-5" aria-hidden="true" /> Mirascope Docs
        </ButtonLink>
        <ButtonLink
          href="https://mirascope.com/discord-invite"
          variant="outline"
          size="default"
          className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] border-0 bg-white px-6 py-4 text-center font-handwriting font-medium text-black hover:bg-gray-100 hover:text-black sm:w-auto"
        >
          <Users className="size-5" aria-hidden="true" /> Join the Community
        </ButtonLink>
      </div>

      {/* Scroll indicator to go back to the top */}
      {onScrollToTop && (
        <div className="mt-8 flex justify-center">
          <div className="landing-page-box-shadow landing-page-box-shadow-hover relative h-10 w-10 overflow-hidden rounded-full">
            <button
              onClick={onScrollToTop}
              className="bg-primary/80 hover:bg-primary absolute inset-0 flex items-center justify-center border-0 transition-all"
              aria-label="Scroll to top"
            >
              <ChevronUp className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export function HomePage() {
  useSunsetTime();
  useGradientFadeOnScroll({ fadeStartDistance: 100, fadeEndDistance: 10 });

  const heroSectionRef = useRef<HTMLDivElement>(null);
  const mirascopeSectionRef = useRef<HTMLDivElement>(null);

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
      const y =
        element.getBoundingClientRect().top + window.pageYOffset + yOffset;

      window.scrollTo({ top: y, behavior: "smooth" });

      // Update URL hash without causing a jump
      window.history.pushState(null, "", "#mirascope");
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
        switch (targetId) {
          case "mirascope":
            scrollToMirascopeSection();
            break;
          case "hero":
            scrollToHeroSection();
            break;
        }
      }, 300);
    }

    // Handle hash changes after page load
    const handleHashChange = () => {
      const currentHash = window.location.hash.substring(1);

      switch (currentHash) {
        case "mirascope":
          scrollToMirascopeSection();
          break;
        case "hero":
          scrollToHeroSection();
          break;
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
        const mirascopePosition =
          mirascopeSectionRef.current?.getBoundingClientRect().top || 0;

        if (
          mirascopePosition < window.innerHeight / 2 &&
          mirascopeSectionRef.current
        ) {
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
      <div className={cn(homeStyles.watercolorBg, "watercolor-bg")}></div>
      {/* todo(seb): Figure out page meta */}
      {/* <PageMeta title="Home" description="The AI Engineer's Developer Stack" /> */}
      <div className="flex w-full flex-col">
        {/* Hero section */}
        <div data-gradient-fade={true} ref={heroSectionRef}>
          <HeroBlock
            onScrollDown={scrollToMirascopeSection}
            showScrollButton={showScrollButton}
          />
        </div>

        {/* Mirascope section */}
        <div
          data-gradient-fade={true}
          ref={mirascopeSectionRef}
          className="mb-24"
        >
          <MirascopeBlock onScrollToTop={scrollToHeroSection} />
        </div>
      </div>
    </>
  );
}
