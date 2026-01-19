import type { ReactNode } from "react";
import { Sidebar } from "@/app/components/sidebar";

type DashboardLayoutProps = {
  children: ReactNode;
};

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex h-[calc(100vh-60px)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-background">{children}</main>
    </div>
  );
}
