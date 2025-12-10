import React from "react";
import type { ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/mirascope-ui/ui/button";
import { ChevronLeft } from "lucide-react";

interface ErrorContentProps {
  title?: string;
  message: string | null;
  showBackButton?: boolean;
  backTo?: string;
  backLabel?: string;
  children?: ReactNode;
}

/**
 * ErrorContent - A reusable error display component
 *
 * Shows error information with optional back button and debug details
 */
const ErrorContent: React.FC<ErrorContentProps> = ({
  title = "Not Found",
  message,
  showBackButton = false,
  backTo = "",
  backLabel = "Back",
  children,
}) => {
  return (
    <div className="min-w-0 flex-1 px-4 py-6">
      <div className="mx-auto max-w-5xl">
        {showBackButton && (
          <div className="mb-6">
            <Link to={backTo} className="inline-block">
              <Button variant="outline" size="sm">
                <ChevronLeft className="mr-1 h-4 w-4" />
                {backLabel}
              </Button>
            </Link>
          </div>
        )}

        <h1 className="mb-4 text-2xl font-medium">{title}</h1>

        {message && <p className="text-muted-foreground mb-4">{message}</p>}

        {children}
      </div>
    </div>
  );
};

export default ErrorContent;
