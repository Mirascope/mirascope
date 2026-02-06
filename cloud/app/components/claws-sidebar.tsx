import { Bot, Plus } from "lucide-react";

import { Button } from "@/app/components/ui/button";

export function ClawsSidebar() {
  return (
    <aside className="w-48 h-full flex flex-col bg-background">
      <div className="px-3 pt-4 pb-2">
        <div className="flex items-center gap-2 mb-3">
          <Bot className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs font-medium text-muted-foreground">
            Lobsters
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3">
        <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-muted/30">
          <p className="text-sm text-muted-foreground">Coming soon</p>
        </div>
      </div>

      <div className="px-3 pb-4">
        <Button variant="outline" size="sm" className="w-full" disabled>
          <Plus className="h-4 w-4 mr-1" />
          New Lobster
        </Button>
      </div>
    </aside>
  );
}
