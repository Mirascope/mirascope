import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import type { FunctionResponse } from "@/api/functions.schemas";

interface FunctionCardProps {
  fn: FunctionResponse;
}

export function FunctionCard({ fn }: FunctionCardProps) {
  const formattedDate = fn.createdAt
    ? new Date(fn.createdAt).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <Card className="group transition-shadow hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="font-mono text-lg">{fn.name}</CardTitle>
          <Badge variant="secondary" size="sm">
            v{fn.version}
          </Badge>
        </div>
        {fn.description && (
          <CardDescription className="line-clamp-2">
            {fn.description}
          </CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {fn.tags && fn.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {fn.tags.map((tag) => (
              <Badge key={tag} variant="outline" size="sm">
                {tag}
              </Badge>
            ))}
          </div>
        )}
        {formattedDate && (
          <div className="text-muted-foreground text-xs">
            Created {formattedDate}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
