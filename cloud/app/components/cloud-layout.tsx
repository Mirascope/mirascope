import type { ReactNode } from "react";
import { Sidebar } from "@/app/components/sidebar";

type CloudLayoutProps = {
  children: ReactNode;
};

export function CloudLayout({ children }: CloudLayoutProps) {
  return (
    <div className="flex h-[calc(100vh-60px)]">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-background">{children}</main>
    </div>
  );
}
