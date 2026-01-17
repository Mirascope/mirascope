import type { ReactNode } from "react";
import { Sidebar } from "@/app/components/sidebar";
import { OrganizationProvider } from "@/app/contexts/organization";

type DashboardLayoutProps = {
  children: ReactNode;
};

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <OrganizationProvider>
      <div className="flex h-[calc(100vh - var(--header-height))]">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-background">{children}</main>
      </div>
    </OrganizationProvider>
  );
}
