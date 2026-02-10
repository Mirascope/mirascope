import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { useState, type FormEvent } from "react";

import { Button } from "@/app/components/ui/button";
import { DialogBody, DialogFooter } from "@/app/components/ui/dialog";
import { getStripe, stripeAppearance } from "@/app/lib/stripe";

interface PaymentFormProps {
  clientSecret: string;
  amount: number;
  onSuccess: () => void;
  onError: (error: string) => void;
  onBack?: () => void;
  children?: React.ReactNode;
}

/**
 * Payment form component that wraps Stripe PaymentElement.
 *
 * Handles payment confirmation and manages loading/error states.
 */
function PaymentForm({
  amount,
  onSuccess,
  onError,
  onBack,
  children,
}: PaymentFormProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: window.location.href,
        },
        redirect: "if_required",
      });

      if (error) {
        setErrorMessage(error.message ?? "An error occurred during payment");
        onError(error.message ?? "An error occurred during payment");
      } else {
        // Payment succeeded
        onSuccess();
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred";
      setErrorMessage(message);
      onError(message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(e)} className="contents">
      <DialogBody className="space-y-4">
        <div className="space-y-2">
          <PaymentElement />
        </div>

        {errorMessage && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {errorMessage}
          </div>
        )}

        <div className="rounded-lg border border-border bg-muted/50 p-3 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Amount to pay:</span>
            <span className="font-semibold">${amount.toFixed(2)}</span>
          </div>
        </div>

        {children}
      </DialogBody>

      <DialogFooter>
        {onBack && (
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
        )}
        <Button
          type="submit"
          disabled={!stripe || isProcessing}
          className={onBack ? "" : "w-full"}
        >
          {isProcessing ? "Processing..." : `Pay $${amount.toFixed(2)}`}
        </Button>
      </DialogFooter>
    </form>
  );
}

/**
 * Router Credits Payment Form with Stripe Elements wrapper.
 *
 * Embeds Stripe's Payment Element for collecting payment information
 * directly in the application. Handles payment confirmation and success/error states.
 */
export function RouterCreditsPaymentForm({
  clientSecret,
  amount,
  onSuccess,
  onError,
  onBack,
  children,
}: PaymentFormProps) {
  const stripePromise = getStripe();

  return (
    <Elements
      stripe={stripePromise}
      options={{
        clientSecret,
        appearance: stripeAppearance,
      }}
    >
      <PaymentForm
        clientSecret={clientSecret}
        amount={amount}
        onSuccess={onSuccess}
        onError={onError}
        onBack={onBack}
      >
        {children}
      </PaymentForm>
    </Elements>
  );
}
