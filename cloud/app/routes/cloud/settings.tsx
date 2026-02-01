import { createFileRoute, Outlet } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SettingsSidebar } from "@/app/components/settings-sidebar";

function CloudSettingsLayout() {
  return (
    <Protected>
      <CloudLayout>
        <div className="flex h-full justify-center">
          <div className="flex h-full w-full max-w-5xl">
            <SettingsSidebar />
            <main className="flex-1 overflow-y-auto p-6">
              <Outlet />
            </main>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/settings")({
  component: CloudSettingsLayout,
});
