import {
  Elements,
  useStripe,
  useElements,
  PaymentElement,
} from "@stripe/react-stripe-js";
import { CreditCard, Loader2, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import {
  usePaymentMethod,
  useCreateSetupIntent,
  useRemovePaymentMethod,
} from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/app/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { getStripe, stripeAppearance } from "@/app/lib/stripe";

interface SavedPaymentMethodProps {
  organizationId: string;
}

function capitalizeCardBrand(brand: string): string {
  const brandMap: Record<string, string> = {
    visa: "Visa",
    mastercard: "Mastercard",
    amex: "Amex",
    discover: "Discover",
    diners: "Diners",
    jcb: "JCB",
    unionpay: "UnionPay",
  };
  return brandMap[brand] ?? brand.charAt(0).toUpperCase() + brand.slice(1);
}

/**
 * Inner form that uses Stripe hooks (must be inside Elements provider).
 */
function SetupForm({
  onSuccess,
  onCancel,
}: {
  onSuccess: () => void;
  onCancel: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const { error } = await stripe.confirmSetup({
        elements,
        confirmParams: {
          return_url: window.location.href,
        },
        redirect: "if_required",
      });

      if (error) {
        setErrorMessage(error.message ?? "Failed to save card");
      } else {
        onSuccess();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setErrorMessage(message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
      <PaymentElement />
      {errorMessage && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
          {errorMessage}
        </div>
      )}
      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isProcessing}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={!stripe || isProcessing}>
          {isProcessing ? "Saving..." : "Save Card"}
        </Button>
      </div>
    </form>
  );
}

export function SavedPaymentMethod({
  organizationId,
}: SavedPaymentMethodProps) {
  const {
    data: paymentMethod,
    isLoading,
    refetch,
  } = usePaymentMethod(organizationId);
  const createSetupIntent = useCreateSetupIntent();
  const removePaymentMethod = useRemovePaymentMethod();

  const [setupDialogOpen, setSetupDialogOpen] = useState(false);
  const [clientSecret, setClientSecret] = useState<string | null>(null);

  const handleAddOrUpdate = async () => {
    try {
      const result = await createSetupIntent.mutateAsync(organizationId);
      setClientSecret(result.clientSecret);
      setSetupDialogOpen(true);
    } catch {
      toast.error("Failed to initialize card setup");
    }
  };

  const handleSetupSuccess = () => {
    setSetupDialogOpen(false);
    setClientSecret(null);
    toast.success("Payment method saved");
    void refetch();
  };

  const handleRemove = () => {
    removePaymentMethod.mutate(organizationId, {
      onSuccess: () => {
        toast.success("Payment method removed");
      },
      onError: () => {
        toast.error("Failed to remove payment method");
      },
    });
  };

  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-start justify-between space-y-0">
          <CardTitle>Payment Method</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={() => void handleAddOrUpdate()}
            disabled={createSetupIntent.isPending}
          >
            {createSetupIntent.isPending
              ? "Loading..."
              : paymentMethod
                ? "Update Card"
                : "Add Card"}
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          ) : paymentMethod ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CreditCard className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium">
                    {capitalizeCardBrand(paymentMethod.brand)} ····
                    {paymentMethod.last4}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Expires {paymentMethod.expMonth}/{paymentMethod.expYear}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRemove}
                disabled={removePaymentMethod.isPending}
              >
                <Trash2 className="h-4 w-4 text-muted-foreground" />
              </Button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              No payment method on file. Add a card to enable one-click
              purchases.
            </p>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={setupDialogOpen}
        onOpenChange={(open) => {
          setSetupDialogOpen(open);
          if (!open) setClientSecret(null);
        }}
      >
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {paymentMethod ? "Update Payment Method" : "Add Payment Method"}
            </DialogTitle>
            <DialogDescription>
              Your card will be saved securely for future purchases.
            </DialogDescription>
          </DialogHeader>
          {clientSecret && (
            <Elements
              stripe={getStripe()}
              options={{
                clientSecret,
                appearance: stripeAppearance,
              }}
            >
              <SetupForm
                onSuccess={handleSetupSuccess}
                onCancel={() => {
                  setSetupDialogOpen(false);
                  setClientSecret(null);
                }}
              />
            </Elements>
          )}
          {!clientSecret && (
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setSetupDialogOpen(false)}
              >
                Close
              </Button>
            </DialogFooter>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
