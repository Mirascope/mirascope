import type { ReactNode } from "react";
import { Sidebar } from "@/app/components/sidebar";
import { OrganizationProvider } from "@/app/contexts/organization";
import { ProjectProvider } from "@/app/contexts/project";
import { EnvironmentProvider } from "@/app/contexts/environment";

type DashboardLayoutProps = {
  children: ReactNode;
};

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <OrganizationProvider>
      <ProjectProvider>
        <EnvironmentProvider>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-background">
              {children}
            </main>
          </div>
        </EnvironmentProvider>
      </ProjectProvider>
    </OrganizationProvider>
  );
}
