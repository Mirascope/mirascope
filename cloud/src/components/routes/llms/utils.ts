export const formatTokenCount = (count: number): string => {
  if (count < 1000) {
    return "<1k";
  }
  const rounded = Math.round(count / 1000);
  return `${rounded}k`;
};

export const tokenBadge =
  "bg-secondary text-secondary-foreground rounded-md px-2 py-0.5 text-xs font-medium";
