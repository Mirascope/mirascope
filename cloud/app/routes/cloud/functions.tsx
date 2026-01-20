import { CloudLayout } from "@/app/components/cloud-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";

function FunctionsPage() {
  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <div className="flex items-center justify-center h-64">
            <p className="text-muted-foreground text-lg">
              Functions Coming Soon...
            </p>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/functions")({
  component: FunctionsPage,
});
