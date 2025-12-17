import React from "react";
import { cn } from "@/app/lib/utils";
import { logoSizeMap } from "@/app/components/blocks/branding/logo-utils";
import type { BaseLogoProps } from "@/app/components/blocks/branding/logo-utils";
import { MIRASCOPE } from "@/app/lib/site";

/**
 * Mirascope Logo component with customizable size and text display
 */
const MirascopeLogo: React.FC<BaseLogoProps> = ({
  size = "medium",
  withText = true,
  className,
  textClassName,
  imgClassName,
  containerClassName,
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
          className={cn(selectedSize.img, imgClassName)}
        />
      </div>

      {withText && (
        <div className={cn("flex items-center", textClassName)}>
          <span
            className={cn(
              selectedSize.text,
              "text-mirascope-purple font-handwriting mb-0",
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
