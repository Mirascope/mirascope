import type { Claw } from "@/api/claws.schemas";

import { Badge } from "@/app/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";

const statusConfig: Record<
  Claw["status"],
  { className: string; label: string }
> = {
  active: {
    className:
      "bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/20",
    label: "Active",
  },
  pending: {
    className:
      "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
    label: "Pending",
  },
  provisioning: {
    className:
      "bg-yellow-500/15 text-yellow-700 dark:text-yellow-400 border-yellow-500/20",
    label: "Provisioning",
  },
  error: {
    className: "bg-red-500/15 text-red-700 dark:text-red-400 border-red-500/20",
    label: "Error",
  },
  paused: {
    className:
      "bg-gray-500/15 text-gray-700 dark:text-gray-400 border-gray-500/20",
    label: "Paused",
  },
};

const instanceSizeLabel: Record<Claw["instanceType"], string> = {
  lite: "Lite",
  basic: "Small",
  "standard-1": "Medium",
  "standard-2": "Medium",
  "standard-3": "Large",
  "standard-4": "XL",
};

interface ClawCardProps {
  claw: Claw;
  onClick?: () => void;
}

export function ClawCard({ claw, onClick }: ClawCardProps) {
  const status = statusConfig[claw.status];

  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-muted/50"
      onClick={onClick}
    >
      <CardHeader className="p-4">
        <CardTitle className="flex items-center gap-2 text-base">
          <span className="truncate">{claw.displayName ?? claw.slug}</span>
          <Badge pill className="shrink-0 font-normal">
            {instanceSizeLabel[claw.instanceType]}
          </Badge>
          <Badge pill className={`shrink-0 ml-auto ${status.className}`}>
            {status.label}
          </Badge>
        </CardTitle>
        <CardDescription className="text-sm truncate">
          {claw.slug}
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
