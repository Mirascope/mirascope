import React from "react";
import { cn } from "@/app/lib/utils";
import { logoSizeMap } from "@/app/components/blocks/branding/logo-utils";
import type { BaseLogoProps } from "@/app/components/blocks/branding/logo-utils";
import { MIRASCOPE } from "@/app/lib/site";

interface MirascopeLogoProps extends BaseLogoProps {
  /** Use white text color (for landing page) */
  lightText?: boolean;
}

/**
 * Mirascope Logo component with customizable size and text display
 */
const MirascopeLogo: React.FC<MirascopeLogoProps> = ({
  size = "medium",
  withText = true,
  className,
  textClassName,
  imgClassName,
  containerClassName,
  lightText = false,
}) => {
  const selectedSize = logoSizeMap[size];
  const logoPath = "/assets/branding/mirascope-logo.svg";

  const logoContent = (
    <div
      className={cn(
        "flex shrink-0 flex-row items-center justify-start",
        containerClassName,
      )}
    >
      <div className={cn(selectedSize.spacing, "shrink-0", imgClassName)}>
        <img
          src={logoPath}
          alt="Mirascope Frog Logo"
          className={cn(
            selectedSize.img,
            imgClassName,
            lightText && "brightness-0 invert",
          )}
        />
      </div>

      {withText && (
        <div className={cn("flex items-center", textClassName)}>
          <span
            className={cn(
              selectedSize.text,
              "font-handwriting mb-0 drop-shadow-md",
              lightText ? "text-white" : "text-mirple",
            )}
          >
            {MIRASCOPE.title}
          </span>
        </div>
      )}
    </div>
  );

  return <div className={className}>{logoContent}</div>;
};

export default MirascopeLogo;
