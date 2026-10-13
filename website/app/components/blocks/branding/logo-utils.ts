/**
 * Shared utilities for logo components
 */

export type LogoSize = "micro" | "small" | "medium" | "large";

export interface LogoSizeConfig {
  container: string;
  img: string;
  text: string;
  spacing: string;
  wrapper: string;
}

/**
 * Size configurations for logos - shared across all product logos
 * for consistent sizing and spacing.
 * Logo image heights are now set to match the text height using CSS variables.
 */
export const logoSizeMap: Record<LogoSize, LogoSizeConfig> = {
  micro: {
    container: "w-auto",
    img: "h-[var(--text-sm)] w-auto",
    text: "text-sm",
    spacing: "mr-1.5",
    wrapper: "px-1.5 py-0.5",
  },
  small: {
    container: "w-auto",
    img: "h-[var(--text-xl)] w-auto",
    text: "text-xl",
    spacing: "mr-2",
    wrapper: "px-4 py-2",
  },
  medium: {
    container: "w-auto",
    img: "h-[var(--text-2xl)] w-auto",
    text: "text-2xl",
    spacing: "mr-3",
    wrapper: "px-5 py-2.5",
  },
  large: {
    container: "w-auto",
    img: "h-[var(--text-4xl)] w-auto",
    text: "text-4xl",
    spacing: "mr-4",
    wrapper: "px-6 py-3",
  },
};

/**
 * Base props shared across all logo components
 */
export interface BaseLogoProps {
  size?: LogoSize;
  withText?: boolean;
  className?: string;
  textClassName?: string;
  imgClassName?: string;
  containerClassName?: string;
}
