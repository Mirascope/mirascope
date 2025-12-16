import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/app/components/blocks/theme-provider";
import { useFontMode } from "@/app/components/blocks/font-mode-provider";
import { Button } from "@/app/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";

export const ModeToggle = () => {
  const { setTheme } = useTheme();
  const { fontMode, setFontMode } = useFontMode();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0" />
          <span className="sr-only">Toggle modes</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Color Theme</DropdownMenuLabel>
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuLabel>Font Mode</DropdownMenuLabel>
        <DropdownMenuItem
          onClick={() => setFontMode("default")}
          className={fontMode === "default" ? "text-primary" : ""}
        >
          Default
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setFontMode("fun")}
          className={fontMode === "fun" ? "text-primary" : ""}
        >
          Fun
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setFontMode("professional")}
          className={fontMode === "professional" ? "text-primary" : ""}
        >
          Professional
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
