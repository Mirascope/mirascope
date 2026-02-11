import { createFileRoute, Outlet } from "@tanstack/react-router";

import { CloudLayout } from "@/app/components/cloud-layout";
import { Protected } from "@/app/components/protected";
import { SettingsSidebar } from "@/app/components/settings-sidebar";

function SettingsLayout() {
  return (
    <Protected>
      <CloudLayout>
        <div className="flex min-h-full justify-center">
          <div className="flex w-full max-w-5xl pl-12">
            <div className="sticky top-0 h-[calc(100vh-60px)] shrink-0">
              <SettingsSidebar />
            </div>
            <div className="flex-1 py-6 pl-6">
              <div className="max-w-3xl">
                <Outlet />
              </div>
            </div>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/settings")({
  component: SettingsLayout,
});
