import type { ReactNode } from "react";
import { Sidebar } from "@/src/components/sidebar";
import { OrganizationProvider } from "@/src/contexts/organization";
import { ProjectProvider } from "@/src/contexts/project";

type DashboardLayoutProps = {
  children: ReactNode;
};

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <OrganizationProvider>
      <ProjectProvider>
        <div className="flex h-screen">
          <Sidebar />
          <main className="flex-1 overflow-y-auto bg-background">
            {children}
          </main>
        </div>
      </ProjectProvider>
    </OrganizationProvider>
  );
}
