import { createFileRoute, Outlet } from "@tanstack/react-router";

import { Protected } from "@/app/components/protected";
import { SettingsSidebar } from "@/app/components/settings-sidebar";

function CloudSettingsLayout() {
  return (
    <Protected>
      <div className="flex h-[calc(100vh-60px)] justify-center bg-background">
        <div className="flex h-full w-full max-w-4xl">
          <SettingsSidebar />
          <main className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/settings")({
  component: CloudSettingsLayout,
});
