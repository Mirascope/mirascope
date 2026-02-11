import { Link } from "@tanstack/react-router";

import type { FunctionResponse } from "@/api/functions.schemas";

import { Badge } from "@/app/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

interface FunctionCardProps {
  fn: FunctionResponse;
}

export function FunctionCard({ fn }: FunctionCardProps) {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { selectedEnvironment } = useEnvironment();
  const orgSlug = selectedOrganization?.slug ?? "";
  const projectSlug = selectedProject?.slug ?? "";
  const envSlug = selectedEnvironment?.slug ?? "";

  const formattedDate = fn.createdAt
    ? new Date(fn.createdAt).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : null;

  return (
    <Link
      to="/$orgSlug/projects/$projectSlug/$envSlug/functions/$functionName"
      params={{ orgSlug, projectSlug, envSlug, functionName: fn.name }}
      className="block"
    >
      <Card className="group cursor-pointer transition-shadow hover:shadow-md">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="font-mono text-lg">{fn.name}</CardTitle>
            <Badge variant="default" size="sm">
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
    </Link>
  );
}
