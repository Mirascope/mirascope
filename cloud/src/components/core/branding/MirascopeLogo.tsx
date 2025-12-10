import React from "react";
import { cn } from "@/src/lib/utils";
import { logoSizeMap } from "./logoUtils";
import type { BaseLogoProps } from "./logoUtils";

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
        "flex flex-shrink-0 flex-row items-center justify-start",
        containerClassName,
      )}
    >
      <div className={cn(selectedSize.spacing, "flex-shrink-0", imgClassName)}>
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
            Mirascope
          </span>
        </div>
      )}
    </div>
  );

  return <div className={className}>{logoContent}</div>;
};

export default MirascopeLogo;
