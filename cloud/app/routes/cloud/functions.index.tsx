import { useMemo } from "react";
import { Loader2, RefreshCw } from "lucide-react";
import { CloudLayout } from "@/app/components/cloud-layout";
import { createFileRoute } from "@tanstack/react-router";
import { Protected } from "@/app/components/protected";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useFunctionsList } from "@/app/api/functions";
import { FunctionCard } from "@/app/components/function-card";
import { Button } from "@/app/components/ui/button";
import type { FunctionResponse } from "@/api/functions.schemas";

/**
 * Compare semantic versions (e.g., "1.0", "1.1", "2.0").
 * Returns positive if a > b, negative if a < b, 0 if equal.
 */
function compareVersions(a: string, b: string): number {
  const [aMajor, aMinor] = a.split(".").map(Number);
  const [bMajor, bMinor] = b.split(".").map(Number);
  if (aMajor !== bMajor) return aMajor - bMajor;
  return (aMinor ?? 0) - (bMinor ?? 0);
}

/**
 * Group functions by name and return only the latest version of each.
 */
function getLatestVersionsByName(
  functions: readonly FunctionResponse[],
): FunctionResponse[] {
  const byName = new Map<string, FunctionResponse>();

  for (const fn of functions) {
    const existing = byName.get(fn.name);
    if (!existing || compareVersions(fn.version, existing.version) > 0) {
      byName.set(fn.name, fn);
    }
  }

  return Array.from(byName.values());
}

function FunctionsPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();

  const { data, isLoading, isFetching, refetch } = useFunctionsList(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    selectedEnvironment?.id ?? null,
  );

  // Group by name and show only the latest version of each function
  const uniqueFunctions = useMemo(() => {
    if (!data?.functions) return [];
    return getLatestVersionsByName(data.functions);
  }, [data?.functions]);

  if (!selectedEnvironment) {
    return (
      <Protected>
        <CloudLayout>
          <div className="p-6">
            <div className="flex h-64 items-center justify-center">
              <p className="text-muted-foreground text-lg">
                Select an environment to view functions.
              </p>
            </div>
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-2xl font-semibold">Functions</h1>
            <Button
              variant="outline"
              size="sm"
              onClick={() => void refetch()}
              disabled={isFetching}
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${isFetching ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>

          {isLoading && (
            <div className="flex h-64 items-center justify-center">
              <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
            </div>
          )}

          {!isLoading && uniqueFunctions.length === 0 && (
            <div className="flex h-64 items-center justify-center">
              <div className="text-center">
                <p className="text-muted-foreground mb-2 text-lg">
                  No functions found in this environment.
                </p>
                <p className="text-muted-foreground text-sm">
                  Functions will appear here when they are registered via the
                  SDK.
                </p>
              </div>
            </div>
          )}

          {!isLoading && uniqueFunctions.length > 0 && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {uniqueFunctions.map((fn) => (
                <FunctionCard key={fn.id} fn={fn} />
              ))}
            </div>
          )}
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/functions/")({
  component: FunctionsPage,
});
