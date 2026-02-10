import { createFileRoute, Outlet } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SettingsSidebar } from "@/app/components/settings-sidebar";

function SettingsLayout() {
  return (
    <Protected>
      <CloudLayout>
        <div className="flex h-full">
          <SettingsSidebar />
          <div className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/$orgSlug/settings")({
  component: SettingsLayout,
});
