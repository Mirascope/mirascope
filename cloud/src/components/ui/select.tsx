import * as React from "react";
import { cn } from "@/src/lib/utils";

export type SelectProps = React.ComponentProps<"select"> & {
  label?: string;
};

export function Select({ className, label, children, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-xs font-medium text-muted-foreground">
          {label}
        </label>
      )}
      <select
        className={cn(
          "h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
        {...props}
      >
        {children}
      </select>
    </div>
  );
}
