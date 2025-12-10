import { ChevronDown, Rocket } from "lucide-react";
import { ButtonLink } from "@/mirascope-ui/ui/button-link";
import { ResponsiveTextBlock } from "@/src/components/ui/responsive-text-block";

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
      <div className="torn-paper-effect absolute inset-0 bg-white"></div>

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

export function HeroBlock({ onScrollDown, showScrollButton }: HeroBlockProps) {
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
            className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] border-0 bg-white text-center font-bold text-black hover:bg-white/90 hover:text-black sm:w-auto"
          >
            <Rocket className="size-5" aria-hidden="true" />
            Mirascope v2 Alpha
          </ButtonLink>
          <ButtonLink
            href="/discord-invite"
            variant="default"
            size="lg"
            className="landing-page-box-shadow landing-page-box-shadow-hover w-full min-w-[200px] bg-[#5865F2] text-center font-bold text-white hover:bg-[#5865F2]/90 sm:w-auto"
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
        className={`fixed right-0 bottom-16 left-0 z-10 flex justify-center transition-opacity duration-300 ${
          showScrollButton ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
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

export { styleSystem };
