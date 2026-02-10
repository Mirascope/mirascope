import { CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import { Link, useNavigate } from "@tanstack/react-router";
import { LogOut, Settings } from "lucide-react";
import { useState } from "react";

import {
  useIsLandingPage,
  useIsLoginPage,
} from "@/app/components/blocks/theme-provider";
import { CreateOrganizationModal } from "@/app/components/create-organization-modal";
import { Button } from "@/app/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/app/components/ui/dropdown-menu";
import { useAuth } from "@/app/contexts/auth";
import { useOrganization } from "@/app/contexts/organization";
import { cn } from "@/app/lib/utils";

interface AccountMenuProps {
  className?: string;
}

// z-index higher than header (z-[100])
const DROPDOWN_Z_INDEX = "z-[110]";

export function AccountMenu({ className }: AccountMenuProps) {
  const { user, logout } = useAuth();
  const {
    organizations,
    selectedOrganization,
    setSelectedOrganization,
    isLoading: orgsLoading,
  } = useOrganization();
  const navigate = useNavigate();
  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const isLandingPage = useIsLandingPage();
  const isLoginPage = useIsLoginPage();
  const isLandingStyle = isLandingPage || isLoginPage;

  const handleSignOut = async () => {
    await logout();
    void navigate({ to: "/" });
  };

  const handleOrgSelect = (orgId: string) => {
    const org = organizations.find((o) => o.id === orgId);
    if (org) {
      setSelectedOrganization(org);
      void navigate({ to: "/$orgSlug", params: { orgSlug: org.slug } });
    }
  };

  // Not authenticated - show Sign In button
  if (!user) {
    return (
      <Link to="/login" className={cn("cursor-pointer", className)}>
        <Button
          variant={isLandingStyle ? "outline" : "default"}
          size="sm"
          className={cn(
            isLandingStyle &&
              "border-white/50 bg-white/10 text-white hover:bg-white/20 hover:border-white/70 hover:text-white",
          )}
        >
          Sign In
        </Button>
      </Link>
    );
  }

  // Authenticated - show organization dropdown
  const hasOrganizations = organizations.length > 0;

  // Determine button text
  const getButtonText = () => {
    if (orgsLoading) return "Loading...";
    if (!hasOrganizations) return "Create Organization";
    return selectedOrganization?.name ?? "Select Organization";
  };

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            className={cn(
              "border-input flex h-9 w-[200px] items-center justify-between rounded-md border bg-transparent px-3 py-2 text-sm shadow-sm",
              isLandingStyle &&
                "border-white/50 bg-white/10 text-white hover:bg-white/20 hover:border-white/70 hover:text-white",
              className,
            )}
          >
            <span className="truncate">{getButtonText()}</span>
            <CaretSortIcon className="h-4 w-4 opacity-50 shrink-0" />
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="end"
          className={cn(
            "w-[200px] bg-popover text-popover-foreground",
            DROPDOWN_Z_INDEX,
          )}
        >
          {/* Organizations */}
          {hasOrganizations ? (
            <DropdownMenuGroup>
              {organizations.map((org) => (
                <DropdownMenuItem
                  key={org.id}
                  onClick={() => handleOrgSelect(org.id)}
                  className="flex items-center justify-between"
                >
                  <span className="truncate">{org.name}</span>
                  {org.id === selectedOrganization?.id && (
                    <CheckIcon className="h-4 w-4 shrink-0" />
                  )}
                </DropdownMenuItem>
              ))}
              <DropdownMenuItem
                onClick={() => setShowCreateOrg(true)}
                className="text-[var(--mirple)] font-medium"
              >
                + New Organization
              </DropdownMenuItem>
            </DropdownMenuGroup>
          ) : (
            <DropdownMenuItem
              onClick={() => setShowCreateOrg(true)}
              className="text-[var(--mirple)] font-medium"
            >
              + New Organization
            </DropdownMenuItem>
          )}

          <DropdownMenuSeparator />

          {/* Settings & Sign Out */}
          <DropdownMenuItem asChild>
            <Link
              to="/$orgSlug/settings"
              params={{ orgSlug: selectedOrganization?.slug ?? "" }}
            >
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => void handleSignOut()}>
            <LogOut className="mr-2 h-4 w-4" />
            Sign Out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <CreateOrganizationModal
        open={showCreateOrg}
        onOpenChange={setShowCreateOrg}
      />
    </>
  );
}
