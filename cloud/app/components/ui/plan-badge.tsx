import { Badge, type BadgeProps } from "@/app/components/ui/badge";
import type { PlanTier } from "@/payments/plans";

const planVariants: Record<PlanTier, string> = {
  free: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
  pro: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  team: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
};

const planLabels: Record<PlanTier, string> = {
  free: "Free",
  pro: "Pro",
  team: "Team",
};

interface PlanBadgeProps extends Omit<BadgeProps, "children"> {
  plan: PlanTier;
  showLabel?: boolean;
}

export function PlanBadge({
  plan,
  showLabel = true,
  className,
  ...props
}: PlanBadgeProps) {
  return (
    <Badge className={`${planVariants[plan]} ${className || ""}`} {...props}>
      {showLabel ? planLabels[plan] : null}
    </Badge>
  );
}

export { planLabels };
