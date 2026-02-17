import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { agent } from "@/lib/agent";
import { MiniCard } from "@/components/mini-card";
import { ClawTable } from "@/components/claw-table";
import { SettingsBar } from "@/components/settings-bar";

export const Route = createFileRoute("/" as never)({
  component: Dashboard,
});

function Dashboard() {
  return (
    <div className="min-h-screen flex flex-col">
      <SettingsBar />
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8 space-y-8">
        <FleetOverview />
        <ClawsSection />
      </main>
    </div>
  );
}

function Header() {
  return (
    <header className="border-b border-gray-800 bg-gray-950">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl">🖥️</span>
          <h1 className="text-lg font-semibold text-gray-100">Fleet Admin</h1>
          <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
            Local
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Polling every 5s
        </div>
      </div>
    </header>
  );
}

function FleetOverview() {
  const { data: health, error, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: agent.health,
  });

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
        <h2 className="text-red-400 font-medium mb-1">Agent Unreachable</h2>
        <p className="text-sm text-red-300/70">{error.message}</p>
        <p className="text-xs text-gray-500 mt-2">
          Make sure the Mac Mini Agent is running. Check the agent URL in the settings bar.
        </p>
      </div>
    );
  }

  if (isLoading || !health) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 animate-pulse">
        <div className="h-4 bg-gray-800 rounded w-48 mb-4" />
        <div className="space-y-3">
          <div className="h-3 bg-gray-800 rounded w-full" />
          <div className="h-3 bg-gray-800 rounded w-3/4" />
          <div className="h-3 bg-gray-800 rounded w-5/6" />
        </div>
      </div>
    );
  }

  return (
    <section>
      <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
        Fleet Overview
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <MiniCard health={health} />
      </div>
    </section>
  );
}

function ClawsSection() {
  const { data, error } = useQuery({
    queryKey: ["claws"],
    queryFn: agent.listClaws,
  });

  return (
    <section>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider">
          Claws
        </h2>
        {data && data.claws.length > 0 && (
          <span className="text-xs text-gray-500">
            {data.claws.length} claw{data.claws.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>
      {error ? (
        <div className="text-sm text-red-400">{error.message}</div>
      ) : (
        <ClawTable claws={data?.claws ?? []} />
      )}
    </section>
  );
}
