import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import * as React from "react";

import { CreateClawModal } from "@/app/components/create-claw-modal";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";

const icons = {
  chat: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
    />
  ),
  secrets: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
    />
  ),
};

function SidebarIcon({ children }: { children: React.ReactNode }) {
  return (
    <svg
      className="w-5 h-5 flex-shrink-0"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      {children}
    </svg>
  );
}

function SidebarLink({
  to,
  params,
  icon,
  label,
  isActive,
}: {
  to: string;
  params: Record<string, string>;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
}) {
  return (
    <Link
      to={to}
      params={params}
      className={`flex items-center gap-3 px-3 py-2 text-base rounded-md text-foreground font-display ${
        isActive ? "bg-primary/10 text-primary font-medium" : "hover:bg-muted"
      }`}
    >
      <SidebarIcon>{icon}</SidebarIcon>
      {label}
    </Link>
  );
}

export function ClawsSidebar() {
  const { selectedOrganization } = useOrganization();
  const { claws, selectedClaw, setSelectedClaw, isLoading } = useClaw();
  const [createModalOpen, setCreateModalOpen] = React.useState(false);
  const navigate = useNavigate();

  const router = useRouterState();
  const currentPath = router.location.pathname;
  const orgSlug = selectedOrganization?.slug ?? "";
  const clawSlug = selectedClaw?.slug ?? "";

  const handleClawSelectChange = (value: string) => {
    if (value === "__create_new__") {
      setCreateModalOpen(true);
      return;
    }
    const claw = claws.find((c) => c.id === value);
    if (claw) {
      setSelectedClaw(claw);
      void navigate({
        to: "/$orgSlug/claws/$clawSlug/chat",
        params: { orgSlug, clawSlug: claw.slug },
      });
    }
  };

  const isActive = (path: string) => {
    if (currentPath === path) return true;
    return currentPath.startsWith(`${path}/`);
  };

  const chatPath = `/${orgSlug}/claws/${clawSlug}/chat`;
  const secretsPath = `/${orgSlug}/claws/${clawSlug}/secrets`;

  return (
    <aside className="w-48 h-full flex flex-col bg-background">
      {/* Claw selector */}
      {selectedOrganization && (
        <div className="px-2 pt-4 pb-2">
          <div className="text-xs font-medium text-muted-foreground mb-1 px-1">
            Claw
          </div>
          {isLoading ? (
            <div className="flex justify-center py-2">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Select
              value={selectedClaw?.id || ""}
              onValueChange={handleClawSelectChange}
            >
              <SelectTrigger className="bg-background text-base">
                <SelectValue placeholder="Select claw" />
              </SelectTrigger>
              <SelectContent>
                {claws.map((claw) => (
                  <SelectItem key={claw.id} value={claw.id}>
                    {claw.displayName ?? claw.slug}
                  </SelectItem>
                ))}
                <SelectItem
                  value="__create_new__"
                  className="text-primary font-medium"
                >
                  + New Claw
                </SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
      )}

      <div className="mx-2 border-t border-border" />

      {/* Navigation links */}
      <div className="px-2 pt-4">
        <SidebarLink
          to="/$orgSlug/claws/$clawSlug/chat"
          params={{ orgSlug, clawSlug }}
          icon={icons.chat}
          label="Chat"
          isActive={isActive(chatPath) && !currentPath.includes("/secrets")}
        />
      </div>

      <div className="flex-1 overflow-y-auto px-2 pt-2 space-y-2">
        <SidebarLink
          to="/$orgSlug/claws/$clawSlug/secrets"
          params={{ orgSlug, clawSlug }}
          icon={icons.secrets}
          label="Secrets"
          isActive={isActive(secretsPath)}
        />
      </div>

      <CreateClawModal
        open={createModalOpen}
        onOpenChange={setCreateModalOpen}
      />
    </aside>
  );
}
