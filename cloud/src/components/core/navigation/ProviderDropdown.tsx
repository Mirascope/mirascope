import { Button } from "@/mirascope-ui/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/src/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import { useProvider, providers, providerDefaults } from "../providers/ProviderContext";
import { cn } from "@/src/lib/utils";

interface ProviderDropdownProps {
  className?: string;
}

export function ProviderDropdown({ className }: ProviderDropdownProps) {
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
              "text-primary border-primary" // Always show the selected provider in primary color
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
                provider === p && "text-primary font-medium"
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
