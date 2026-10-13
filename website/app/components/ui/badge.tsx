import * as React from "react";

const badgeVariants = {
  variant: {
    default:
      "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
    secondary:
      "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
    neutral: "bg-background hover:bg-background/80",
    destructive:
      "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
    outline: "text-foreground",
  },
  size: {
    default: "px-2.5 py-0.5 text-xs",
    sm: "px-2 py-1 text-xs",
    lg: "px-3 py-1 text-sm",
  },
  shape: {
    default: "rounded-md",
    pill: "rounded-full",
  },
};

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: keyof typeof badgeVariants.variant;
  size?: keyof typeof badgeVariants.size;
  pill?: boolean;
}

function Badge({
  className = "",
  variant = "default",
  size = "default",
  pill = false,
  ...props
}: BadgeProps) {
  const shapeClass = pill
    ? badgeVariants.shape.pill
    : badgeVariants.shape.default;
  const baseClasses = `inline-flex items-center ${shapeClass} border font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2`;
  const variantClasses = badgeVariants.variant[variant];
  const sizeClasses = badgeVariants.size[size];

  const combinedClasses = `${baseClasses} ${variantClasses} ${sizeClasses} ${className}`;

  return <div className={combinedClasses} {...props} />;
}

export { Badge, badgeVariants };
