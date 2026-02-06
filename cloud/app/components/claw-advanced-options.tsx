import { ChevronDownIcon } from "@radix-ui/react-icons";
import { useState } from "react";

import type { CreateClawRequest } from "@/api/claws.schemas";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/app/components/ui/collapsible";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { cn } from "@/app/lib/utils";

const MODELS = [
  {
    value: "claude-haiku-4-5",
    label: "Claude Haiku 4.5",
    hint: "Most efficient — uses the fewest credits per request",
  },
  {
    value: "claude-sonnet-4-5",
    label: "Claude Sonnet 4.5",
    hint: "Balanced — uses moderate credits for greater intelligence",
  },
  {
    value: "claude-opus-4-6",
    label: "Claude Opus 4.6",
    hint: "Most capable — uses significantly more credits per request",
  },
] as const;

interface ClawAdvancedOptionsProps {
  model: CreateClawRequest["model"];
  onModelChange: (model: CreateClawRequest["model"]) => void;
  weeklyGuardrail: string;
  onWeeklyGuardrailChange: (value: string) => void;
}

export function ClawAdvancedOptions({
  model,
  onModelChange,
  weeklyGuardrail,
  onWeeklyGuardrailChange,
}: ClawAdvancedOptionsProps) {
  const [isOpen, setIsOpen] = useState(false);
  const selectedModel = MODELS.find((m) => m.value === model);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <CollapsibleTrigger className="flex w-full items-center gap-1 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors py-2">
        <ChevronDownIcon
          className={cn("h-4 w-4 transition-transform", isOpen && "rotate-180")}
        />
        Advanced Options
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="space-y-4 rounded-md border p-4">
          {/* Model selector */}
          <div className="space-y-2">
            <Label htmlFor="claw-model">Model</Label>
            <Select
              value={model}
              onValueChange={(v) =>
                onModelChange(v as CreateClawRequest["model"])
              }
            >
              <SelectTrigger id="claw-model">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {MODELS.map((m) => (
                  <SelectItem key={m.value} value={m.value}>
                    {m.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedModel && (
              <p className="text-xs text-muted-foreground">
                {selectedModel.hint}
              </p>
            )}
          </div>

          {/* Weekly guardrail */}
          <div className="space-y-2">
            <Label htmlFor="claw-guardrail">
              Weekly request guardrail{" "}
              <span className="text-muted-foreground font-normal">
                (optional)
              </span>
            </Label>
            <Input
              id="claw-guardrail"
              type="number"
              min={0}
              placeholder="e.g. 100"
              value={weeklyGuardrail}
              onChange={(e) => onWeeklyGuardrailChange(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">
              Pause this claw after roughly this many requests per week. Leave
              empty for no per-claw limit.
            </p>
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
