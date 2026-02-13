import { Link } from "@tanstack/react-router";

import { useIsWatercolorPage } from "@/app/components/blocks/theme-provider";
import { cn } from "@/app/lib/utils";

export default function Footer() {
  const isWatercolorPage = useIsWatercolorPage();

  return (
    <footer
      className={cn(
        "relative z-50 mt-auto w-full px-4 pt-4 pb-3 sm:px-6 md:px-12",
        isWatercolorPage ? "bg-transparent text-white" : "bg-background",
      )}
    >
      <div className="mx-auto flex max-w-5xl flex-col-reverse items-center justify-between md:flex-row md:items-center">
        <div className="mt-4 text-center text-sm sm:text-base md:mt-0 md:text-left font-handwriting">
          <p>© {new Date().getFullYear()} Mirascope. All rights reserved.</p>
          <p>
            Mirascope® is a registered trademark of Mirascope, Inc. in the U.S.
          </p>
        </div>

        <div className="flex gap-4 sm:gap-8">
          <Link
            to="/privacy"
            className={cn(
              "text-sm sm:text-base",
              isWatercolorPage ? "text-white hover:text-white/80" : "nav-text",
            )}
          >
            <span className="text-sm sm:text-base font-handwriting">
              Privacy Policy
            </span>
          </Link>
          <Link
            to="/terms/$"
            params={{ _splat: "use" }}
            className={cn(
              "text-sm sm:text-base",
              isWatercolorPage ? "text-white hover:text-white/80" : "nav-text",
            )}
          >
            <span className="text-sm sm:text-base font-handwriting">
              Terms of Use
            </span>
          </Link>
        </div>
      </div>
    </footer>
  );
}
