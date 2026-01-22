import { cn } from "@/app/lib/utils";
import { useSunsetTime } from "@/app/hooks/sunset-time";
import { BookOpen } from "lucide-react";
import { ButtonLink } from "@/app/components/ui/button-link";
import DiscordInviteButton from "@/app/components/blocks/branding/discord-invite-button";
import homeStyles from "@/app/components/home-page.module.css";
import { ResponsiveTextBlock } from "@/app/components/blocks/responsive-text-block";
import { UnifiedDemo } from "@/app/components/landing/unified-demo";

// Shared styling constants for logo and hero components
// This ensures we maintain consistency and makes future updates easier
const styleSystem = {
  // Base dimensions for different components
  logoFontSize: "clamp(1.75rem, 4.5vw, 3.5rem)", // Smaller than hero text
  heroFontSize: "clamp(1.75rem, 5.5vw, 4.5rem)", // Responsive hero text
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
            className="font-handwriting text-mirple"
          >
            Mirascope
          </h1>
        </div>
      </div>
    </div>
  );
};

// Hero block component with logo and text
function HeroBlock() {
  return (
    <div className="relative">
      {/* Container that holds all hero content */}
      <div className="relative z-10 flex flex-col items-center px-4 pt-8 pb-8">
        {/* Content wrapper */}
        <div className="flex flex-col items-center">
          <div
            style={{
              marginBottom: logoStyles.logoToHeroSpacing,
            }}
          >
            <LogoBanner />
          </div>

          <div className="text-center">
            <ResponsiveTextBlock
              lines={["Build. Observe. Iterate. Ship."]}
              fontSize={styleSystem.heroFontSize}
              className="flex flex-col font-medium tracking-tight text-white"
              lineClassName="font-handwriting"
              textShadow={true}
            />
          </div>
        </div>

        {/* Subtitle */}
        <div className="mt-6 text-center">
          <p className="font-handwriting text-lg text-white/90 text-shade sm:text-2xl md:text-4xl">
            The complete toolkit for AI engineers
          </p>
        </div>

        {/* Interactive demo block */}
        <div className="mt-8 w-full max-w-5xl px-4">
          <UnifiedDemo />
        </div>

        <div className="mt-8 flex w-full max-w-3xl flex-col items-center justify-center gap-4 sm:flex-row">
          <ButtonLink
            href="/docs"
            variant="outline"
            size="lg"
            className="box-shade w-full min-w-[200px] border-0 bg-white text-center font-handwriting font-bold text-black hover:bg-white/90 hover:text-black sm:w-auto"
          >
            <BookOpen className="size-5" aria-hidden="true" />
            Mirascope Docs
          </ButtonLink>
          <DiscordInviteButton
            variant="default"
            size="lg"
            className="box-shade w-full min-w-[200px] bg-mirple text-center font-handwriting font-bold text-white hover:bg-mirple-dark/90 sm:w-auto"
          >
            Join our
            <img
              src="/assets/branding/Discord-Logo-White.svg"
              alt="Discord"
              className="h-3.5 w-auto"
            />
          </DiscordInviteButton>
        </div>
      </div>
    </div>
  );
}
export function HomePage() {
  useSunsetTime();

  return (
    <>
      <div className={cn(homeStyles.watercolorBg, "watercolor-bg")}></div>
      <div className="flex w-full flex-col">
        <HeroBlock />
      </div>
    </>
  );
}
