import { Button as EmailButton } from "@react-email/components";
import * as React from "react";

interface ButtonProps {
  href: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * Branded button component for email templates.
 *
 * A reusable call-to-action button with Mirascope brand colors and styling.
 * Supports custom style overrides while maintaining consistent defaults.
 *
 * @param href - The URL to link to
 * @param children - Button text content
 * @param style - Optional style overrides
 */
export function Button({ href, children, style }: ButtonProps) {
  const defaultStyle = {
    backgroundColor: "#6366f1",
    borderRadius: "8px",
    color: "#ffffff",
    fontSize: "16px",
    fontWeight: "600",
    textDecoration: "none",
    textAlign: "center" as const,
    display: "inline-block",
    padding: "12px 24px",
  };

  return (
    <EmailButton href={href} style={{ ...defaultStyle, ...style }}>
      {children}
    </EmailButton>
  );
}
