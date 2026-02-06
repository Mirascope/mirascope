import type { Claw } from "@/api/claws.schemas";

import { Badge } from "@/app/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";

const statusColor: Record<Claw["status"], string> = {
  active: "bg-green-500",
  pending: "bg-yellow-500",
  provisioning: "bg-yellow-500",
  error: "bg-red-500",
  paused: "bg-gray-400",
};

interface ClawCardProps {
  claw: Claw;
  onClick?: () => void;
}

export function ClawCard({ claw, onClick }: ClawCardProps) {
  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-muted/50"
      onClick={onClick}
    >
      <CardHeader className="p-4">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span
              className={`h-2 w-2 shrink-0 rounded-full ${statusColor[claw.status]}`}
            />
            <CardTitle className="text-base truncate">
              {claw.displayName ?? claw.slug}
            </CardTitle>
          </div>
          <Badge variant="secondary" size="sm">
            {claw.instanceType}
          </Badge>
        </div>
        <CardDescription className="text-sm truncate pl-4">
          {claw.slug}
        </CardDescription>
      </CardHeader>
      {claw.description && (
        <CardContent className="px-4 pb-3 pt-0">
          <p className="text-muted-foreground text-xs line-clamp-2">
            {claw.description}
          </p>
        </CardContent>
      )}
    </Card>
  );
}
