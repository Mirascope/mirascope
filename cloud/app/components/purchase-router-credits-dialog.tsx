import { useQueryClient } from "@tanstack/react-query";
import { CreditCard } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { toast } from "sonner";

import {
  useCreatePaymentIntent,
  usePaymentMethod,
} from "@/app/api/organizations";
import { RouterCreditsPaymentForm } from "@/app/components/router-credits-payment-form";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/app/components/ui/dialog";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { getStripe } from "@/app/lib/stripe";

interface PurchaseRouterCreditsDialogProps {
  organizationId: string;
  currentBalance: number;
  trigger?: React.ReactNode;
}

const PRESET_AMOUNTS = [10, 25, 50, 100];

type Step = "select-amount" | "payment" | "success";

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

export function PurchaseRouterCreditsDialog({
  organizationId,
  currentBalance,
  trigger,
}: PurchaseRouterCreditsDialogProps) {
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<Step>("select-amount");
  const [amount, setAmount] = useState(50);
  const [customAmount, setCustomAmount] = useState("");
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [useDifferentCard, setUseDifferentCard] = useState(false);

  const queryClient = useQueryClient();
  const createPaymentIntent = useCreatePaymentIntent();
  const { data: paymentMethod } = usePaymentMethod(organizationId);

  const useSavedCard = paymentMethod && !useDifferentCard;

  // Track polling interval for cleanup
  const pollingIntervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const finalAmount = customAmount ? parseFloat(customAmount) : amount;

  const handleContinueToPayment = async () => {
    if (finalAmount <= 0 || isNaN(finalAmount)) {
      toast.error("Please enter a valid amount");
      return;
    }

    try {
      const result = await createPaymentIntent.mutateAsync({
        organizationId,
        data: {
          amount: finalAmount,
          paymentMethodId: useSavedCard ? paymentMethod.id : undefined,
        },
      });

      if (result.status === "succeeded") {
        // Server-side confirmation succeeded (saved card, no 3DS)
        handlePaymentSuccess();
        return;
      }

      if (result.status === "requires_action" && result.clientSecret) {
        // 3DS required — use Stripe.js to handle
        const stripe = await getStripe();
        if (!stripe) {
          toast.error("Stripe failed to load");
          return;
        }

        const { error } = await stripe.confirmPayment({
          clientSecret: result.clientSecret,
          confirmParams: {
            return_url: window.location.href,
          },
          redirect: "if_required",
        });

        if (error) {
          toast.error(error.message ?? "Payment authentication failed");
        } else {
          handlePaymentSuccess();
        }
        return;
      }

      // No saved card — show payment form
      setClientSecret(result.clientSecret);
      setStep("payment");
    } catch (error) {
      toast.error("Failed to create payment intent. Please try again.");
      console.error("Payment intent error:", error);
    }
  };

  const handlePaymentSuccess = () => {
    setStep("success");

    // Clear any existing polling
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    // Immediately refetch once
    void queryClient.refetchQueries({
      queryKey: ["organizations", organizationId, "router-balance"],
    });

    // Poll every 1 second for webhook to process (up to 10 seconds)
    let pollCount = 0;
    pollingIntervalRef.current = setInterval(() => {
      void queryClient.refetchQueries({
        queryKey: ["organizations", organizationId, "router-balance"],
      });
      pollCount++;
      if (pollCount >= 10) {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
      }
    }, 1000);

    // Close dialog after showing success message
    setTimeout(() => {
      setOpen(false);

      // Reset state for next time
      setTimeout(() => {
        setStep("select-amount");
        setClientSecret(null);
        setCustomAmount("");
        setAmount(50);
        setUseDifferentCard(false);
      }, 300);
    }, 2000);
  };

  const handlePaymentError = (error: string) => {
    toast.error(`Payment failed: ${error}`);
  };

  const handleBack = () => {
    setStep("select-amount");
    setClientSecret(null);
  };

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    if (!newOpen) {
      // Stop polling when dialog closes
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      // Reset state when closing
      setTimeout(() => {
        setStep("select-amount");
        setClientSecret(null);
        setCustomAmount("");
        setAmount(50);
        setUseDifferentCard(false);
      }, 300);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger ?? <Button variant="default">Purchase Credits</Button>}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        {step === "select-amount" && (
          <>
            <DialogHeader>
              <DialogTitle>Purchase Router Credits</DialogTitle>
              <DialogDescription>
                Add credits to your account to use Mirascope Router. Current
                balance:{" "}
                <span className="font-semibold">
                  ${currentBalance.toFixed(2)}
                </span>
              </DialogDescription>
            </DialogHeader>
            <DialogBody className="grid gap-4">
              <div className="space-y-2">
                <Label>Select Amount</Label>
                <div className="grid grid-cols-4 gap-2">
                  {PRESET_AMOUNTS.map((presetAmount) => (
                    <Button
                      key={presetAmount}
                      type="button"
                      variant={
                        amount === presetAmount && !customAmount
                          ? "default"
                          : "outline"
                      }
                      onClick={() => {
                        setAmount(presetAmount);
                        setCustomAmount("");
                      }}
                    >
                      ${presetAmount}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="custom-amount">Or Enter Custom Amount</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                    $
                  </span>
                  <Input
                    id="custom-amount"
                    type="number"
                    placeholder="0.00"
                    min="1"
                    step="0.01"
                    value={customAmount}
                    onChange={(e) => setCustomAmount(e.target.value)}
                    className="pl-7"
                  />
                </div>
              </div>
              <div className="rounded-lg border border-border bg-muted/50 p-3 text-sm">
                <div className="flex justify-between mb-1">
                  <span className="text-muted-foreground">Amount:</span>
                  <span className="font-medium">${finalAmount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">New Balance:</span>
                  <span className="font-semibold">
                    ${(currentBalance + finalAmount).toFixed(2)}
                  </span>
                </div>
              </div>

              {paymentMethod && (
                <div className="flex items-center justify-between rounded-lg border border-border bg-muted/50 p-3 text-sm">
                  <div className="flex items-center gap-2">
                    <CreditCard className="h-4 w-4 text-muted-foreground" />
                    <span>
                      {useSavedCard
                        ? `Paying with ${capitalizeCardBrand(paymentMethod.brand)} ····${paymentMethod.last4}`
                        : "Using new payment method"}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="text-xs text-primary underline hover:no-underline"
                    onClick={() => setUseDifferentCard(!useDifferentCard)}
                  >
                    {useSavedCard
                      ? "Use different card"
                      : `Use ${capitalizeCardBrand(paymentMethod.brand)} ····${paymentMethod.last4}`}
                  </button>
                </div>
              )}
            </DialogBody>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                disabled={createPaymentIntent.isPending}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={() => void handleContinueToPayment()}
                disabled={createPaymentIntent.isPending}
              >
                {createPaymentIntent.isPending
                  ? "Processing..."
                  : useSavedCard
                    ? `Pay $${finalAmount.toFixed(2)} with ${capitalizeCardBrand(paymentMethod.brand)} ····${paymentMethod.last4}`
                    : "Continue to Payment"}
              </Button>
            </DialogFooter>
          </>
        )}

        {step === "payment" && clientSecret && (
          <>
            <DialogHeader>
              <DialogTitle>Enter Payment Details</DialogTitle>
              <DialogDescription>
                Complete your purchase of ${finalAmount.toFixed(2)} in router
                credits
              </DialogDescription>
            </DialogHeader>
            <RouterCreditsPaymentForm
              clientSecret={clientSecret}
              amount={finalAmount}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
              onBack={handleBack}
            >
              <p className="text-xs text-muted-foreground">
                Your card will be saved for future purchases.
              </p>
            </RouterCreditsPaymentForm>
          </>
        )}

        {step === "success" && (
          <>
            <DialogHeader>
              <DialogTitle>Payment Successful!</DialogTitle>
              <DialogDescription>
                Your credits have been added to your account
              </DialogDescription>
            </DialogHeader>
            <div className="px-6 py-6 text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                <svg
                  className="h-6 w-6 text-green-600 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <p className="text-lg font-semibold mb-1">
                ${finalAmount.toFixed(2)} added to your account
              </p>
              <p className="text-sm text-muted-foreground">
                This dialog will close automatically
              </p>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
