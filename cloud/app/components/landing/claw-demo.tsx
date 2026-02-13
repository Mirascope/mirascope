import { useCallback, useState } from "react";

import { cn } from "@/app/lib/utils";

import { ClawDemoChat } from "./claw-demo-chat";
import { ClawDemoDeploy } from "./claw-demo-deploy";
import { ClawDemoIntegrate } from "./claw-demo-integrate";

const TABS = [
  { id: "deploy", label: "Deploy" },
  { id: "integrate", label: "Integrate" },
  { id: "interact", label: "Interact" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export function ClawDemo({ className }: { className?: string }) {
  const [activeTab, setActiveTab] = useState<TabId>("deploy");
  // Increment to force remount of sub-components on tab re-entry
  const [cycle, setCycle] = useState(0);

  const advanceTab = useCallback(() => {
    setActiveTab((current) => {
      const idx = TABS.findIndex((t) => t.id === current);
      return TABS[(idx + 1) % TABS.length].id;
    });
    setCycle((c) => c + 1);
  }, []);

  const handleTabClick = (tabId: TabId) => {
    if (tabId === activeTab) return;
    setActiveTab(tabId);
    setCycle((c) => c + 1);
  };

  return (
    <div
      className={cn(
        "flex w-full flex-col overflow-hidden rounded-lg border border-slate-200 bg-white shadow-lg dark:border-border dark:bg-background",
        className,
      )}
    >
      {/* Tab bar */}
      <div className="flex border-b border-slate-200 bg-slate-50 dark:border-border dark:bg-primary/5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className={cn(
              "flex-1 px-2 py-2 text-center font-display text-sm transition-colors",
              activeTab === tab.id
                ? "border-b-2 border-mirple font-semibold text-mirple"
                : "text-slate-500 hover:text-slate-700 dark:text-muted-foreground dark:hover:text-foreground",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content — fixed height on mobile, grows to fill on desktop */}
      <div data-demo-scroll className="min-h-0 flex-1 overflow-y-auto">
        {activeTab === "deploy" && (
          <ClawDemoDeploy
            key={`deploy-${cycle}`}
            isActive={true}
            onComplete={advanceTab}
          />
        )}
        {activeTab === "interact" && (
          <ClawDemoChat
            key={`interact-${cycle}`}
            isActive={true}
            onComplete={advanceTab}
          />
        )}
        {activeTab === "integrate" && (
          <ClawDemoIntegrate
            key={`integrate-${cycle}`}
            isActive={true}
            onComplete={advanceTab}
          />
        )}
      </div>
    </div>
  );
}
