import { useEffect, useRef, useState } from "react";

import { ClawIcon } from "@/app/components/icons/claw-icon";
import { ClawDemo } from "@/app/components/landing/claw-demo";
import { TypingAnimation } from "@/app/components/landing/typing-animation";
import { ValueProps } from "@/app/components/landing/value-props";
import { ButtonLink } from "@/app/components/ui/button-link";
import { WatercolorBackground } from "@/app/components/watercolor-background";
import { useSunsetTime } from "@/app/hooks/sunset-time";

export function HomePage() {
  useSunsetTime();

  const heroRef = useRef<HTMLDivElement>(null);
  const [heroHeight, setHeroHeight] = useState<number | null>(null);

  useEffect(() => {
    const el = heroRef.current;
    if (!el) return;
    const observer = new ResizeObserver(([entry]) => {
      setHeroHeight(entry.contentRect.height);
    });
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <>
      <WatercolorBackground />
      <div className="flex grow flex-col items-center justify-center">
        {/* Hero + Demo row */}
        <div className="mx-auto flex w-full max-w-5xl flex-col items-center gap-6 px-4 lg:flex-row lg:gap-12 lg:px-8">
          {/* Left: headline, subtitle, CTA */}
          <div
            ref={heroRef}
            className="flex w-full max-w-xl flex-col items-center text-center lg:items-start lg:text-left"
          >
            {/* Headline */}
            <h1
              className="font-handwriting font-medium tracking-tight text-white text-shade"
              style={{
                fontSize: "clamp(2.75rem, 8vw, 4rem)",
                lineHeight: "1.15",
              }}
            >
              Chatbots chat.
              <br />
              Claws <TypingAnimation />
            </h1>

            {/* Subtitle */}
            <p
              className="mt-4 font-handwriting font-semibold text-white lg:mt-5 [text-shadow:0_2px_8px_rgba(0,0,0,0.3),0_4px_16px_rgba(0,0,0,0.15)]"
              style={{ fontSize: "clamp(1.25rem, 4vw, 1.75rem)" }}
            >
              <span className="inline-block whitespace-nowrap">
                Stop repeating yourself.
              </span>{" "}
              <span className="inline-block whitespace-nowrap">
                Your Claw remembers.
              </span>
            </p>

            {/* CTAs */}
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:gap-4 lg:mt-7">
              <ButtonLink
                href="/login"
                size="lg"
                className="box-shade min-h-[48px] min-w-[200px] border-0 bg-mirple font-handwriting font-bold text-white hover:bg-mirple-dark/90 hover:text-white"
              >
                <ClawIcon className="size-5" />
                Deploy Your First Claw
              </ButtonLink>
              <ButtonLink
                href="/pricing"
                variant="outline"
                size="lg"
                className="box-shade min-h-[48px] min-w-[150px] border-0 bg-white font-handwriting font-bold text-black hover:bg-white/90 hover:text-black"
              >
                See Pricing
              </ButtonLink>
            </div>
          </div>

          {/* Right: demo — height matches hero on desktop */}
          <div
            className="w-full max-w-md min-h-fit"
            style={
              heroHeight
                ? { height: Math.round((heroHeight * 5) / 6) }
                : undefined
            }
          >
            <ClawDemo className="h-full" />
          </div>
        </div>

        {/* Value props */}
        <div className="mt-10 shrink-0 lg:mt-24">
          <ValueProps />
        </div>
      </div>
    </>
  );
}
