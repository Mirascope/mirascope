import { AlertCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { centicentsToDollars } from "@/api/router/cost-utils";
import {
  useAutoReloadSettings,
  useOrganizationRouterBalance,
  usePaymentMethod,
  useUpdateAutoReloadSettings,
} from "@/app/api/organizations";
import { PurchaseRouterCreditsDialog } from "@/app/components/purchase-router-credits-dialog";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { Separator } from "@/app/components/ui/separator";
import { Switch } from "@/app/components/ui/switch";

/** Preset threshold options (displayed as dollars, stored as centicents). */
const THRESHOLD_OPTIONS = [
  { centicents: 0n, label: "$0" },
  { centicents: 50000n, label: "$5" },
  { centicents: 100000n, label: "$10" },
  { centicents: 250000n, label: "$25" },
];

/** Preset reload amount options (displayed as dollars, stored as centicents). */
const AMOUNT_OPTIONS = [
  { centicents: 100000n, label: "$10" },
  { centicents: 250000n, label: "$25" },
  { centicents: 500000n, label: "$50" },
  { centicents: 1000000n, label: "$100" },
];

interface RouterCreditsSettingsProps {
  organizationId: string;
}

export function RouterCreditsSettings({
  organizationId,
}: RouterCreditsSettingsProps) {
  const { data: routerBalance, isLoading } =
    useOrganizationRouterBalance(organizationId);
  const { data: autoReload } = useAutoReloadSettings(organizationId);
  const { data: paymentMethod } = usePaymentMethod(organizationId);
  const updateAutoReload = useUpdateAutoReloadSettings();

  const balanceInDollars = routerBalance
    ? centicentsToDollars(routerBalance.balance)
    : 0;

  const handleAutoReloadChange = (updates: {
    enabled?: boolean;
    thresholdCenticents?: bigint;
    amountCenticents?: bigint;
  }) => {
    if (!autoReload) return;

    updateAutoReload.mutate(
      {
        organizationId,
        data: {
          enabled: updates.enabled ?? autoReload.enabled,
          thresholdCenticents:
            updates.thresholdCenticents ?? autoReload.thresholdCenticents,
          amountCenticents:
            updates.amountCenticents ?? autoReload.amountCenticents,
        },
      },
      {
        onSuccess: () => {
          toast.success("Auto-reload settings updated");
        },
        onError: () => {
          toast.error("Failed to update auto-reload settings");
        },
      },
    );
  };

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
              `$${balanceInDollars.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
            )}
          </p>
        </div>
        <p className="text-sm text-muted-foreground mt-4">
          Credits are consumed with Mirascope Router API usage.
          <br />
          They expire 1 year after purchase, and usage includes a 5% gas fee.
          <br />
          By purchasing credits you agree to{" "}
          <a
            href="/terms/credits"
            className="text-primary underline hover:no-underline"
          >
            Mirascope's Credit Terms
          </a>
          .
        </p>

        <Separator className="my-6" />

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Auto-Reload</p>
            <p className="text-sm text-muted-foreground">
              Automatically purchase credits when balance is low
            </p>
          </div>
          <Switch
            checked={autoReload?.enabled ?? false}
            onCheckedChange={(checked) =>
              handleAutoReloadChange({ enabled: checked })
            }
            disabled={!autoReload || updateAutoReload.isPending}
          />
        </div>

        {autoReload?.enabled && (
          <div className="mt-4 space-y-4">
            <div className="flex items-center justify-between">
              <label
                htmlFor="auto-reload-threshold"
                className="text-sm text-muted-foreground"
              >
                When balance falls below
              </label>
              <Select
                value={String(autoReload.thresholdCenticents)}
                onValueChange={(v) =>
                  handleAutoReloadChange({
                    thresholdCenticents: BigInt(v),
                  })
                }
                disabled={updateAutoReload.isPending}
              >
                <SelectTrigger id="auto-reload-threshold" className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {THRESHOLD_OPTIONS.map((opt) => (
                    <SelectItem
                      key={String(opt.centicents)}
                      value={String(opt.centicents)}
                    >
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <label
                htmlFor="auto-reload-amount"
                className="text-sm text-muted-foreground"
              >
                Reload amount
              </label>
              <Select
                value={String(autoReload.amountCenticents)}
                onValueChange={(v) =>
                  handleAutoReloadChange({
                    amountCenticents: BigInt(v),
                  })
                }
                disabled={updateAutoReload.isPending}
              >
                <SelectTrigger id="auto-reload-amount" className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {AMOUNT_OPTIONS.map((opt) => (
                    <SelectItem
                      key={String(opt.centicents)}
                      value={String(opt.centicents)}
                    >
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {!paymentMethod && (
              <div className="flex items-center gap-2 text-sm text-amber-600">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <p>Add a payment method to enable auto-reload</p>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
