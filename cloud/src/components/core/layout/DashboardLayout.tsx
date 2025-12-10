import type { ReactNode } from "react";

/**
 * DashboardLayout - Very simple layout component that centers the content in the middle of the page.
 * This is a work in progress and will be expanded in the future.
 *
 */
const DashboardLayout = ({ children }: { children: ReactNode }) => {
  return (
    <div className="w-full min-h-[calc(60vh-var(--header-height))] grid place-items-center p-8">
      {children}
    </div>
  );
};

export default DashboardLayout;
