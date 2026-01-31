import { ChevronDown, ChevronUp, Copy, Check, Search } from "lucide-react";
import { useEffect, useState, useMemo } from "react";

import ViewModeSwitcher from "@/app/components/blocks/navigation/view-mode-switcher";
import { useViewMode } from "@/app/components/blocks/theme-provider";
import { Badge } from "@/app/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/app/components/ui/collapsible";
import { Input } from "@/app/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import { highlightCode, fallbackHighlighter } from "@/app/lib/code-highlight";
import { cn } from "@/app/lib/utils";

// Types matching the registry JSON structure
interface RegistryIndexItem {
  name: string;
  type: string;
  path: string;
  description?: string;
}

interface RegistryIndex {
  name: string;
  version: string;
  homepage: string;
  items: RegistryIndexItem[];
}

// Type badge colors
const TYPE_COLORS: Record<string, string> = {
  tool: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  agent: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  prompt: "bg-green-500/10 text-green-500 border-green-500/20",
  integration: "bg-orange-500/10 text-orange-500 border-orange-500/20",
};

// Available filter types
const FILTER_TYPES = ["all", "tool", "agent", "prompt", "integration"] as const;
type FilterType = (typeof FILTER_TYPES)[number];

/**
 * Copy button with feedback
 */
function CopyButton({ text, className }: { text: string; className?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Silently fail - button just doesn't show "copied" state
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={cn(
        "text-muted-foreground hover:text-foreground inline-flex items-center gap-1 transition-colors",
        className,
      )}
      title="Copy to clipboard"
    >
      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
    </button>
  );
}

/**
 * Individual registry item card with expandable details
 */
function RegistryCard({ item }: { item: RegistryIndexItem }) {
  const [isOpen, setIsOpen] = useState(false);

  const pythonCommand = `mirascope registry add ${item.name}`;
  const tsCommand = `npx mirascope registry add ${item.name}`;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className="transition-shadow hover:shadow-md">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0 flex-1">
              <CardTitle className="flex items-center gap-2 text-lg">
                {item.name}
                <Badge
                  variant="outline"
                  className={cn("text-xs", TYPE_COLORS[item.type])}
                >
                  {item.type}
                </Badge>
              </CardTitle>
              {item.description && (
                <CardDescription className="mt-1.5 line-clamp-2">
                  {item.description}
                </CardDescription>
              )}
            </div>
            <CollapsibleTrigger asChild>
              <button className="text-muted-foreground hover:text-foreground shrink-0 p-1 transition-colors">
                {isOpen ? (
                  <ChevronUp className="h-5 w-5" />
                ) : (
                  <ChevronDown className="h-5 w-5" />
                )}
              </button>
            </CollapsibleTrigger>
          </div>
        </CardHeader>

        <CollapsibleContent>
          <CardContent className="space-y-3 pt-2">
            <div className="space-y-2">
              <p className="text-muted-foreground text-sm font-medium">
                Install
              </p>
              <div className="space-y-2">
                <div className="bg-muted flex items-center justify-between gap-2 rounded-md px-3 py-2">
                  <code className="text-sm">{pythonCommand}</code>
                  <CopyButton text={pythonCommand} />
                </div>
                <div className="bg-muted flex items-center justify-between gap-2 rounded-md px-3 py-2">
                  <code className="text-sm">{tsCommand}</code>
                  <CopyButton text={tsCommand} />
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Badge variant="secondary" className="text-xs">
                Python
              </Badge>
              <Badge variant="secondary" className="text-xs">
                TypeScript
              </Badge>
            </div>
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}

/**
 * Generate markdown content for MACHINE mode.
 *
 * NOTE: This content should be kept in sync with:
 * 1. `public/registry.md` (the static markdown file served at /registry.md)
 *
 * Unlike the pricing page, `public/registry.md` is AUTO-GENERATED by the
 * registry build script (`scripts/registry/build.ts`). When items are added
 * to the registry, running `bun run registry:build` will regenerate both the
 * JSON files and registry.md automatically.
 *
 * This function generates markdown dynamically from the fetched registry data,
 * ensuring MACHINE mode always reflects the current registry state.
 */
function generateMarkdown(registry: RegistryIndex): string {
  const itemsByType: Record<string, RegistryIndexItem[]> = {};

  for (const item of registry.items) {
    if (!itemsByType[item.type]) {
      itemsByType[item.type] = [];
    }
    itemsByType[item.type].push(item);
  }

  const sections = Object.entries(itemsByType)
    .map(([type, items]) => {
      const itemLines = items
        .map(
          (item) =>
            `- **${item.name}**: ${item.description || "No description"}\n  Install: \`mirascope registry add ${item.name}\``,
        )
        .join("\n");
      return `### ${type.charAt(0).toUpperCase() + type.slice(1)}s\n\n${itemLines}`;
    })
    .join("\n\n");

  return `# Mirascope Registry

Version: ${registry.version}

Browse and install reusable AI components for your Mirascope projects.

## Available Items

${sections || "No items available yet."}

## Installation

**Python:**
\`\`\`bash
mirascope registry add <item-name>
\`\`\`

**TypeScript:**
\`\`\`bash
npx mirascope registry add <item-name>
\`\`\`

## Programmatic Access

Registry index: ${registry.homepage}/r/index.json

For more information, visit: ${registry.homepage}
`;
}

/**
 * Machine-readable registry content with syntax highlighting
 */
function MachineRegistryContent({ registry }: { registry: RegistryIndex }) {
  const [highlightedHtml, setHighlightedHtml] = useState<string | null>(null);
  const markdown = useMemo(() => generateMarkdown(registry), [registry]);

  useEffect(() => {
    let cancelled = false;

    highlightCode(markdown, "markdown")
      .then((result) => {
        if (!cancelled) {
          setHighlightedHtml(result.themeHtml);
        }
      })
      .catch(() => {
        if (!cancelled) {
          const fallback = fallbackHighlighter(markdown, "markdown");
          setHighlightedHtml(fallback.themeHtml);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [markdown]);

  if (!highlightedHtml) {
    const fallback = fallbackHighlighter(markdown, "markdown");
    return (
      <div className="mx-auto max-w-4xl px-4 py-4">
        <div
          className="machine-mode-code highlight-container w-full overflow-auto rounded-md border text-sm [&>pre]:overflow-x-auto [&>pre]:py-3 [&>pre]:pr-5 [&>pre]:pl-4"
          dangerouslySetInnerHTML={{ __html: fallback.themeHtml }}
        />
        <ViewModeSwitcher />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-4">
      <div
        className="machine-mode-code highlight-container w-full overflow-auto rounded-md border text-sm [&>pre]:overflow-x-auto [&>pre]:py-3 [&>pre]:pr-5 [&>pre]:pl-4"
        dangerouslySetInnerHTML={{ __html: highlightedHtml }}
      />
      <ViewModeSwitcher />
    </div>
  );
}

/**
 * Loading skeleton for the registry
 */
function RegistryLoadingSkeleton() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-4">
      <div className="mb-8 text-center">
        <div className="bg-muted mx-auto mb-2 h-10 w-64 animate-pulse rounded" />
        <div className="bg-muted mx-auto h-4 w-96 animate-pulse rounded" />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-muted h-32 animate-pulse rounded-lg" />
        ))}
      </div>
      <ViewModeSwitcher />
    </div>
  );
}

/**
 * Error state for the registry
 */
function RegistryError({ error }: { error: string }) {
  return (
    <div className="mx-auto max-w-4xl px-4 py-4">
      <div className="text-center">
        <h1 className="text-foreground mb-4 text-3xl font-bold">
          Registry Unavailable
        </h1>
        <p className="text-muted-foreground mb-4">
          Unable to load the registry. Please try again later.
        </p>
        <p className="text-destructive text-sm">{error}</p>
      </div>
      <ViewModeSwitcher />
    </div>
  );
}

/**
 * HUMAN mode registry content
 */
function HumanRegistryContent({ registry }: { registry: RegistryIndex }) {
  const [filter, setFilter] = useState<FilterType>("all");
  const [search, setSearch] = useState("");

  const filteredItems = useMemo(() => {
    return registry.items.filter((item) => {
      const matchesType = filter === "all" || item.type === filter;
      const matchesSearch =
        search === "" ||
        item.name.toLowerCase().includes(search.toLowerCase()) ||
        item.description?.toLowerCase().includes(search.toLowerCase());
      return matchesType && matchesSearch;
    });
  }, [registry.items, filter, search]);

  // Count items by type for the filter tabs
  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = { all: registry.items.length };
    for (const item of registry.items) {
      counts[item.type] = (counts[item.type] || 0) + 1;
    }
    return counts;
  }, [registry.items]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-4">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-foreground mb-2 text-4xl font-bold">
          Mirascope Registry
        </h1>
        <p className="text-muted-foreground mb-1">
          Browse and install reusable AI components
        </p>
        <p className="text-muted-foreground text-sm">
          Version {registry.version}
        </p>
      </div>

      {/* Filters and Search */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <Tabs
          value={filter}
          onValueChange={(value) => setFilter(value as FilterType)}
        >
          <TabsList>
            {FILTER_TYPES.map((type) => (
              <TabsTrigger key={type} value={type} className="capitalize">
                {type}
                {typeCounts[type] !== undefined && typeCounts[type] > 0 && (
                  <span className="text-muted-foreground ml-1 text-xs">
                    ({typeCounts[type]})
                  </span>
                )}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>

        <div className="relative w-full sm:w-64">
          <Search className="text-muted-foreground absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" />
          <Input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Items Grid */}
      {filteredItems.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {filteredItems.map((item) => (
            <RegistryCard key={item.name} item={item} />
          ))}
        </div>
      ) : (
        <div className="py-12 text-center">
          <p className="text-muted-foreground">
            {search || filter !== "all"
              ? "No items match your filters."
              : "No items in the registry yet."}
          </p>
        </div>
      )}

      {/* Footer */}
      <div className="text-muted-foreground mt-12 text-center text-sm">
        <p>
          Programmatic access:{" "}
          <a
            href="/r/index.json"
            className="text-primary hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            /r/index.json
          </a>
        </p>
      </div>

      <ViewModeSwitcher />
    </div>
  );
}

/**
 * Main Registry Page component with HUMAN/MACHINE mode support
 */
export function RegistryPage() {
  const viewMode = useViewMode();
  const [registry, setRegistry] = useState<RegistryIndex | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchRegistry() {
      try {
        const response = await fetch("/r/index.json");
        if (!response.ok) {
          throw new Error(`Failed to fetch registry: ${response.status}`);
        }
        const data = (await response.json()) as RegistryIndex;
        if (!cancelled) {
          setRegistry(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Unknown error occurred",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    fetchRegistry();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <RegistryLoadingSkeleton />;
  }

  if (error || !registry) {
    return <RegistryError error={error || "Failed to load registry"} />;
  }

  // In MACHINE mode, render markdown content for AI agents
  if (viewMode === "machine") {
    return <MachineRegistryContent registry={registry} />;
  }

  // In HUMAN mode, render the full interactive page
  return <HumanRegistryContent registry={registry} />;
}
