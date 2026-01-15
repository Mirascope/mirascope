import { Badge, type BadgeProps } from "@/app/components/ui/badge";
import type { InvitationStatus } from "@/api/organization-invitations.schemas";

const statusVariants: Record<InvitationStatus, string> = {
  pending:
    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  revoked: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
};

interface InvitationStatusBadgeProps extends Omit<BadgeProps, "children"> {
  status: InvitationStatus;
}

export function InvitationStatusBadge({
  status,
  className,
  ...props
}: InvitationStatusBadgeProps) {
  return (
    <Badge
      className={`${statusVariants[status]} ${className || ""}`}
      {...props}
    >
      {status}
    </Badge>
  );
}
