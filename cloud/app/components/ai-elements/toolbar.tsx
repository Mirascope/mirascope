import type { ComponentProps } from "react";

import { NodeToolbar, Position } from "@xyflow/react";

import { cn } from "@/app/lib/utils";

type ToolbarProps = ComponentProps<typeof NodeToolbar>;

export const Toolbar = ({ className, ...props }: ToolbarProps) => (
  <NodeToolbar
    className={cn(
      "flex items-center gap-1 rounded-sm border bg-background p-1.5",
      className,
    )}
    position={Position.Bottom}
    {...props}
  />
);
