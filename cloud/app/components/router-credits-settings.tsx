import { useOrganizationRouterBalance } from "@/app/api/organizations";
import { centicentsToDollars } from "@/api/router/cost-utils";
import { PurchaseRouterCreditsDialog } from "@/app/components/purchase-router-credits-dialog";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";
import { Loader2 } from "lucide-react";

interface RouterCreditsSettingsProps {
  organizationId: string;
}

export function RouterCreditsSettings({
  organizationId,
}: RouterCreditsSettingsProps) {
  const { data: routerBalance, isLoading } =
    useOrganizationRouterBalance(organizationId);

  const balanceInDollars = routerBalance
    ? centicentsToDollars(routerBalance.balance)
    : 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0">
        <CardTitle>Mirascope Router Credits</CardTitle>
        {routerBalance && (
          <PurchaseRouterCreditsDialog
            organizationId={organizationId}
            currentBalance={balanceInDollars}
          />
        )}
      </CardHeader>
      <CardContent>
        <div>
          <p className="text-sm text-muted-foreground mb-1">Current Balance</p>
          <p className="text-2xl font-semibold">
            {isLoading ? (
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            ) : (
              `$${balanceInDollars.toFixed(2)}`
            )}
          </p>
        </div>
        <p className="text-sm text-muted-foreground mt-4">
          Credits are consumed with Mirascope Router API usage and expire 1 year
          after purchase.
          <br />
          By purchasing credits you agree to{" "}
          <a
            href="/cloud/terms/router-credits"
            className="text-primary underline hover:no-underline"
          >
            Mirascope's Credit Terms
          </a>
          .
        </p>
      </CardContent>
    </Card>
  );
}
