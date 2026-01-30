import { useTheme } from "@/app/components/blocks/theme-provider";
import { Switch } from "@/app/components/ui/switch";
import { cn } from "@/app/lib/utils";

/**
 * Floating view mode switcher that appears in the bottom right corner
 * Shows on hover for content pages (docs, blog, etc.)
 */
export default function ViewModeSwitcher() {
  const { viewMode, setViewMode } = useTheme();

  const isMachineMode = viewMode === "machine";

  return (
    <div className="fixed bottom-6 right-6 z-[160] group">
      {/* Hover target area - larger than visible element */}
      <div
        className={cn(
          "flex items-center gap-2 rounded-full px-4 py-2",
          "bg-background/90 backdrop-blur-sm border border-border shadow-lg",
          "transition-all duration-300 ease-in-out",
          "opacity-70 hover:opacity-100",
          "cursor-pointer",
        )}
      >
        <button
          type="button"
          onClick={() => setViewMode("human")}
          className={cn(
            "font-handwriting text-sm transition-colors select-none cursor-pointer",
            !isMachineMode
              ? "text-mirple font-semibold"
              : "text-muted-foreground hover:text-mirple/70",
          )}
        >
          HUMAN
        </button>
        <Switch
          checked={isMachineMode}
          onCheckedChange={(checked) =>
            setViewMode(checked ? "machine" : "human")
          }
          className="data-[state=checked]:bg-mirple data-[state=unchecked]:bg-mirple/40"
          aria-label="Toggle between human and machine view mode"
        />
        <button
          type="button"
          onClick={() => setViewMode("machine")}
          className={cn(
            "font-mono text-sm transition-colors select-none cursor-pointer",
            isMachineMode
              ? "text-mirple font-semibold"
              : "text-muted-foreground hover:text-mirple/70",
          )}
        >
          MACHINE
        </button>
      </div>
    </div>
  );
}
