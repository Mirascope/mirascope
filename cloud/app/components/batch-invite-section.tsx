import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Plus, X, Send, Loader2 } from "lucide-react";
import { useCreateInvitation } from "@/app/api/organization-invitations";
import { toast } from "sonner";
import type { InvitationRole } from "@/api/organization-invitations.schemas";

/**
 * Parse invitation errors and return user-friendly messages.
 */
function parseInvitationError(error: unknown): string {
  if (!(error instanceof Error)) {
    return "Failed to send invitation";
  }

  const message = error.message;

  // Plan limit exceeded
  if (
    message.includes("PlanLimitExceededError") ||
    message.includes("plan limit")
  ) {
    return "You've reached your plan's seat limit. Upgrade your plan to invite more members.";
  }

  // Already a member
  if (
    message.includes("already a member") ||
    message.includes("AlreadyExistsError")
  ) {
    return "This user is already a member of this organization";
  }

  // Pending invitation exists
  if (message.includes("pending invitation")) {
    return "A pending invitation already exists for this email";
  }

  // Permission denied
  if (
    message.includes("PermissionDeniedError") ||
    message.includes("permission")
  ) {
    return "You don't have permission to invite members with this role";
  }

  // Invalid email
  if (message.includes("Invalid email")) {
    return "Invalid email format";
  }

  // Default to the original message if it's reasonably short, otherwise generic
  if (message.length < 100 && !message.includes("at ")) {
    return message;
  }

  return "Failed to send invitation";
}

interface InviteRow {
  id: string;
  email: string;
  role: InvitationRole;
  error?: string;
}

interface BatchInviteSectionProps {
  organizationId: string;
  canInviteAdmin: boolean;
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function BatchInviteSection({
  organizationId,
  canInviteAdmin,
}: BatchInviteSectionProps) {
  const [invites, setInvites] = useState<InviteRow[]>([
    { id: crypto.randomUUID(), email: "", role: "MEMBER" },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const createInvitation = useCreateInvitation();

  const addRow = () => {
    setInvites([
      ...invites,
      { id: crypto.randomUUID(), email: "", role: "MEMBER" },
    ]);
  };

  const removeRow = (id: string) => {
    if (invites.length > 1) {
      setInvites(invites.filter((inv) => inv.id !== id));
    }
  };

  const updateRow = (id: string, field: "email" | "role", value: string) => {
    setInvites(
      invites.map((inv) =>
        inv.id === id ? { ...inv, [field]: value, error: undefined } : inv,
      ),
    );
  };

  const validateEmail = (email: string): string | null => {
    if (!email.trim()) {
      return null; // Empty emails will be filtered out
    }
    if (!EMAIL_REGEX.test(email)) {
      return "Invalid email format";
    }
    return null;
  };

  const handleSubmit = async () => {
    // Validate and filter invites
    const validInvites: InviteRow[] = [];
    const updatedInvites = invites.map((invite) => {
      const email = invite.email.trim();
      if (!email) {
        return invite; // Skip empty rows
      }
      const error = validateEmail(email);
      if (error) {
        return { ...invite, error };
      }
      validInvites.push(invite);
      return invite;
    });

    setInvites(updatedInvites);

    if (validInvites.length === 0) {
      toast.error("Please enter at least one valid email");
      return;
    }

    setIsSubmitting(true);
    let successCount = 0;
    const failedInvites: string[] = [];

    for (const invite of validInvites) {
      try {
        await createInvitation.mutateAsync({
          organizationId,
          data: {
            recipientEmail: invite.email.trim(),
            role: invite.role,
          },
        });
        successCount++;
        // Clear successful row
        setInvites((prev) =>
          prev.map((inv) =>
            inv.id === invite.id
              ? { ...inv, email: "", error: undefined }
              : inv,
          ),
        );
      } catch (error) {
        failedInvites.push(invite.id);
        const errorMessage = parseInvitationError(error);
        setInvites((prev) =>
          prev.map((inv) =>
            inv.id === invite.id ? { ...inv, error: errorMessage } : inv,
          ),
        );
        // If it's a plan limit error, stop trying to send more invites
        if (
          errorMessage.includes("plan limit") ||
          errorMessage.includes("upgrade")
        ) {
          break;
        }
      }
    }

    setIsSubmitting(false);

    if (successCount > 0) {
      toast.success(
        `${successCount} invitation${successCount > 1 ? "s" : ""} sent successfully`,
      );
    }

    if (failedInvites.length > 0) {
      toast.error(
        `${failedInvites.length} invitation${failedInvites.length > 1 ? "s" : ""} failed`,
      );
    }

    // Reset to single empty row if all successful
    if (failedInvites.length === 0) {
      setInvites([{ id: crypto.randomUUID(), email: "", role: "MEMBER" }]);
    }
  };

  const hasValidInput = invites.some((inv) => inv.email.trim().length > 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Invite Team Members</CardTitle>
        <CardDescription>
          Send invitations to add new members to your organization. Invitations
          expire in 7 days.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {invites.map((invite) => (
          <div key={invite.id} className="flex items-start gap-3">
            <div className="flex-1">
              <Input
                type="email"
                placeholder="email@example.com"
                value={invite.email}
                onChange={(e) => updateRow(invite.id, "email", e.target.value)}
                className={invite.error ? "border-destructive" : ""}
                disabled={isSubmitting}
              />
              {invite.error && (
                <p className="text-sm text-destructive mt-1">{invite.error}</p>
              )}
            </div>
            <Select
              value={invite.role}
              onValueChange={(value) => updateRow(invite.id, "role", value)}
              disabled={isSubmitting}
            >
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="MEMBER">Member</SelectItem>
                {canInviteAdmin && <SelectItem value="ADMIN">Admin</SelectItem>}
              </SelectContent>
            </Select>
            {invites.length > 1 && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeRow(invite.id)}
                disabled={isSubmitting}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        ))}

        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={addRow} disabled={isSubmitting}>
            <Plus className="h-4 w-4 mr-2" />
            Add another
          </Button>
          <Button
            onClick={() => void handleSubmit()}
            disabled={isSubmitting || !hasValidInput}
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            Send invites
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
