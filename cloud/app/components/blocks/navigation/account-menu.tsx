import { CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import { Link, useNavigate } from "@tanstack/react-router";
import { LogOut, Settings } from "lucide-react";
import { useRef, useState } from "react";

import type { PlanTier } from "@/payments/plans";

import { useDeleteOrganization } from "@/app/api/organizations";
import { useIsWatercolorPage } from "@/app/components/blocks/theme-provider";
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
import { UpgradePlanDialog } from "@/app/components/upgrade-plan-dialog";
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
  const [upgradeNewOrg, setUpgradeNewOrg] = useState<{
    orgId: string;
    orgSlug: string;
    plan: PlanTier;
  } | null>(null);
  const upgradeSucceededRef = useRef(false);
  const deleteOrganization = useDeleteOrganization();
  const isWatercolorPage = useIsWatercolorPage();

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
          variant={isWatercolorPage ? "outline" : "default"}
          size="sm"
          className={cn(
            isWatercolorPage &&
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
              isWatercolorPage &&
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
            <Link to="/settings">
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
        onCreated={(org, planTier) => {
          if (planTier !== "free") {
            // Show upgrade dialog to collect payment for the paid plan
            setUpgradeNewOrg({
              orgId: org.id,
              orgSlug: org.slug,
              plan: planTier,
            });
          } else {
            void navigate({
              to: "/settings/organizations/$orgSlug",
              params: { orgSlug: org.slug },
            });
          }
        }}
      />

      {upgradeNewOrg && (
        <UpgradePlanDialog
          organizationId={upgradeNewOrg.orgId}
          targetPlan={upgradeNewOrg.plan}
          open={true}
          onUpgradeSuccess={() => {
            upgradeSucceededRef.current = true;
          }}
          onOpenChange={(open) => {
            if (!open) {
              const { orgId, orgSlug } = upgradeNewOrg;
              setUpgradeNewOrg(null);

              if (upgradeSucceededRef.current) {
                // Payment succeeded — navigate to the new org
                upgradeSucceededRef.current = false;
                void navigate({
                  to: "/settings/organizations/$orgSlug",
                  params: { orgSlug },
                });
              } else {
                // User dismissed without paying — delete the orphaned org
                void deleteOrganization.mutateAsync(orgId).catch(() => {
                  // Cleanup failed — orphan cron will catch it
                  console.warn(
                    `Failed to clean up org ${orgId} after cancelled payment`,
                  );
                });
              }
            }
          }}
        />
      )}
    </>
  );
}
