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
import { Switch } from "@/app/components/ui/switch";
import { cn } from "@/app/lib/utils";

const MODELS = [
  {
    value: "anthropic/claude-haiku-4-5",
    label: "Claude Haiku 4.5",
    hint: "Most efficient — uses the fewest credits per request",
  },
  {
    value: "anthropic/claude-sonnet-4-5",
    label: "Claude Sonnet 4.5",
    hint: "Balanced — uses moderate credits for greater intelligence",
  },
  {
    value: "anthropic/claude-opus-4-6",
    label: "Claude Opus 4.6",
    hint: "Most capable — uses significantly more credits per request",
  },
] as const;

interface ClawAdvancedOptionsProps {
  model: CreateClawRequest["model"];
  onModelChange: (model: CreateClawRequest["model"]) => void;
  useBeyondPlan: boolean;
  onUseBeyondPlanChange: (value: boolean) => void;
  weeklySpendingLimit: string;
  onWeeklySpendingLimitChange: (value: string) => void;
}

export function ClawAdvancedOptions({
  model,
  onModelChange,
  useBeyondPlan,
  onUseBeyondPlanChange,
  weeklySpendingLimit,
  onWeeklySpendingLimitChange,
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

          {/* Beyond-plan spending guardrail */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label htmlFor="claw-beyond-plan">
                Use router credits beyond included plan
              </Label>
              <Switch
                id="claw-beyond-plan"
                checked={useBeyondPlan}
                onCheckedChange={onUseBeyondPlanChange}
              />
            </div>
            {useBeyondPlan && (
              <div className="space-y-2">
                <Label htmlFor="claw-spending-limit">
                  Weekly spending limit (dollars)
                </Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    $
                  </span>
                  <Input
                    id="claw-spending-limit"
                    type="number"
                    min={0}
                    step="0.01"
                    placeholder="5.00"
                    value={weeklySpendingLimit}
                    onChange={(e) =>
                      onWeeklySpendingLimitChange(e.target.value)
                    }
                    className="pl-7"
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Allow up to this dollar amount per week from purchased router
                  credits when the included plan is exhausted.
                </p>
              </div>
            )}
            {!useBeyondPlan && (
              <p className="text-xs text-muted-foreground">
                When disabled, this claw will stop when the included plan
                credits are exhausted.
              </p>
            )}
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}
