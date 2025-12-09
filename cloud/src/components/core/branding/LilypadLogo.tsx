import React from "react";
import { cn } from "@/src/lib/utils";
import { logoSizeMap } from "./logoUtils";
import type { BaseLogoProps } from "./logoUtils";

interface LilypadLogoProps extends BaseLogoProps {
  showBeta?: boolean;
  betaClassName?: string;
}

/**
 * Lilypad Logo component with customizable size, text display, and beta badge
 */
const LilypadLogo: React.FC<LilypadLogoProps> = ({
  size = "medium",
  withText = true,
  showBeta = true,
  className,
  textClassName,
  imgClassName,
  containerClassName,
  betaClassName,
}) => {
  const selectedSize = logoSizeMap[size];
  const logoPath = "/assets/branding/lilypad-logo.svg";

  // Size-specific beta badge styles
  const betaSizeMap = {
    micro: "text-[8px] px-1 ml-0.5",
    small: "text-[10px] px-1.5 ml-1",
    medium: "text-xs px-2 ml-1.5",
    large: "text-sm px-2.5 ml-2",
  };

  const logoContent = (
    <div
      className={cn("flex flex-shrink-0 flex-row items-center justify-start", containerClassName)}
    >
      <div className={cn(selectedSize.spacing, imgClassName)}>
        <img src={logoPath} alt="Lilypad Logo" className={cn(selectedSize.img, imgClassName)} />
      </div>

      {withText && (
        <div className={cn("flex items-center", textClassName)}>
          <span className={cn(selectedSize.text, "text-lilypad-green font-handwriting mb-0")}>
            Lilypad
          </span>

          {showBeta && (
            <span
              className={cn(
                "rounded-md bg-yellow-400 py-0.5 leading-none font-semibold text-white",
                "font-handwriting flex items-center justify-center",
                betaSizeMap[size],
                betaClassName
              )}
            >
              Beta
            </span>
          )}
        </div>
      )}
    </div>
  );

  return <div className={className}>{logoContent}</div>;
};

export default LilypadLogo;
