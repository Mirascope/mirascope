import { Loader2 } from "lucide-react";

import { centicentsToDollars } from "@/api/router/cost-utils";
import { useOrganizationRouterBalance } from "@/app/api/organizations";
import { PurchaseRouterCreditsDialog } from "@/app/components/purchase-router-credits-dialog";
import { useOrganization } from "@/app/contexts/organization";

export function NavbarCredits() {
  const { selectedOrganization } = useOrganization();
  const { data: routerBalance, isLoading } = useOrganizationRouterBalance(
    selectedOrganization?.id,
  );

  if (!selectedOrganization) return null;

  const balanceInDollars = routerBalance
    ? centicentsToDollars(routerBalance.balance)
    : 0;

  if (isLoading && !routerBalance) {
    return (
      <div className="flex items-center gap-1.5 px-2">
        <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <PurchaseRouterCreditsDialog
      organizationId={selectedOrganization.id}
      currentBalance={balanceInDollars}
      trigger={
        <button className="flex items-center gap-1.5 rounded-md border border-primary/30 bg-primary/5 px-3 py-1.5 text-sm text-foreground transition-colors hover:border-primary/50 hover:bg-primary/10">
          <span className="font-semibold">${balanceInDollars.toFixed(2)}</span>
        </button>
      }
    />
  );
}
