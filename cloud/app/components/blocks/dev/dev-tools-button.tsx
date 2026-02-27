import { Link } from "@tanstack/react-router";
import React from "react";

import { isDevelopment } from "@/app/lib/site";
import { cn } from "@/app/lib/utils";

interface DevToolsButtonProps {
  className?: string;
}

const DevToolsButton: React.FC<DevToolsButtonProps> = ({ className }) => {
  if (!isDevelopment()) {
    return null;
  }

  return (
    <Link
      to="/dev"
      className={cn(
        "border-primary text-accent-foreground bg-background hover:bg-accent hover:text-primary-foreground inline-flex items-center justify-center rounded-md border px-4 py-1 text-sm font-medium shadow-sm",
        className,
      )}
    >
      Dev
    </Link>
  );
};

export default DevToolsButton;
