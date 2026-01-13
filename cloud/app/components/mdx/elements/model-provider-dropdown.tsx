import { Button } from "@/app/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import {
  useProvider,
  providers,
  providerDefaults,
} from "@/app/components/mdx/elements/model-provider-provider";
import { cn } from "@/app/lib/utils";

interface ProviderDropdownProps {
  className?: string;
}

export function ModelProviderDropdown({ className }: ProviderDropdownProps) {
  const { provider, setProvider } = useProvider();

  return (
    <div className={cn("flex flex-col", className)}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            className={cn(
              "w-full justify-between text-base",
              "text-primary border-primary", // Always show the selected provider in primary color
            )}
          >
            {providerDefaults[provider].displayName}
            <ChevronDown className="ml-2 h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-[200px]">
          {providers.map((p) => (
            <DropdownMenuItem
              key={p}
              onClick={() => setProvider(p)}
              className={cn(
                "text-foreground cursor-pointer text-base",
                provider === p && "text-primary font-medium",
              )}
            >
              {providerDefaults[p].displayName}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
