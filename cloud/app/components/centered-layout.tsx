import type { ReactNode } from "react";

// Centers content in the middle of the page.
export function CenteredLayout({ children }: { children: ReactNode }) {
  return (
    <div className="w-full min-h-[calc(100vh-var(--header-height))] grid place-items-center p-8">
      {children}
    </div>
  );
}
