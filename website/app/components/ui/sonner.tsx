import { useTheme } from "next-themes";
import * as React from "react";
import { Toaster as Sonner } from "sonner";

type ToasterProps = React.ComponentProps<typeof Sonner>;

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = "system" } = useTheme();

  return (
    <Sonner
      theme={theme as ToasterProps["theme"]}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:!bg-white group-[.toaster]:dark:!bg-background group-[.toaster]:!text-slate-900 group-[.toaster]:dark:!text-foreground group-[.toaster]:!border-slate-200 group-[.toaster]:dark:!border-border group-[.toaster]:shadow-lg",
          description:
            "group-[.toast]:!text-slate-600 group-[.toast]:dark:!text-foreground/70",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground",
          success: "[&_[data-icon]>svg]:text-emerald-500",
          error: "[&_[data-icon]>svg]:text-red-500",
          warning: "[&_[data-icon]>svg]:text-amber-500",
          info: "[&_[data-icon]>svg]:text-indigo-500",
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
