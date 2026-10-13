import { cva, type VariantProps } from "class-variance-authority";
import { X } from "lucide-react";
import * as React from "react";

import { Button } from "@/app/components/ui/button";
import { cn } from "@/app/lib/utils";

const alertVariants = cva(
  "relative w-full rounded-lg border px-4 py-3 text-sm [&:has(svg)]:pl-11 [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground",
  {
    variants: {
      variant: {
        default: "bg-background text-foreground",
        destructive:
          "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
        warning:
          "border-amber-500/50 bg-amber-50 text-amber-700 dark:border-amber-500/30 dark:bg-amber-900/30 dark:text-amber-400 [&>svg]:text-amber-500",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

const alertCloseButtonVariants = cva("absolute top-2 right-2 h-6 w-6 p-0", {
  variants: {
    variant: {
      default: "hover:bg-muted/80",
      destructive: "hover:bg-destructive/20 text-destructive",
      warning:
        "hover:bg-amber-100 dark:hover:bg-amber-800/30 text-amber-800 dark:text-amber-400",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

interface AlertProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof alertVariants> {
  onClose?: () => void;
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant, children, onClose, ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    >
      {children}
      {onClose && (
        <Button
          size="icon"
          variant="ghost"
          onClick={onClose}
          className={cn(alertCloseButtonVariants({ variant }))}
          aria-label="Close alert"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  ),
);
Alert.displayName = "Alert";

const AlertTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h5
    ref={ref}
    className={cn("mb-1 leading-none font-medium tracking-tight", className)}
    {...props}
  />
));
AlertTitle.displayName = "AlertTitle";

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm [&_p]:leading-relaxed", className)}
    {...props}
  />
));
AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription, AlertTitle };
