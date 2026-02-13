import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { useState, type FormEvent } from "react";

import type { Organization } from "@/api/organizations.schemas";
import type { PlanTier } from "@/payments/plans";

import {
  useCreateOrganization,
  useCreateOrgSetupIntent,
} from "@/app/api/organizations";
import { Button } from "@/app/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { useAnalytics } from "@/app/contexts/analytics";
import { useOrganization } from "@/app/contexts/organization";
import { getErrorMessage } from "@/app/lib/errors";
import { getStripe, stripeAppearance } from "@/app/lib/stripe";
import { generateSlug } from "@/db/slug";

const PLAN_OPTIONS: { value: PlanTier; label: string; description: string }[] =
  [
    {
      value: "free",
      label: "Free",
      description: "For personal projects",
    },
    {
      value: "pro",
      label: "Pro",
      description: "For professional use",
    },
    {
      value: "team",
      label: "Team",
      description: "For teams and collaboration",
    },
  ];

type Step = "details" | "payment";

/**
 * Inner payment form that uses Stripe hooks (must be inside Elements provider).
 */
function PaymentStep({
  orgName,
  orgSlug,
  planTier,
  onSuccess,
  onBack,
}: {
  orgName: string;
  orgSlug: string;
  planTier: PlanTier;
  onSuccess: (org: Organization) => void;
  onBack: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const createOrganization = useCreateOrganization();
  const { setSelectedOrganization } = useOrganization();
  const analytics = useAnalytics();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setIsProcessing(true);
    setError(null);

    try {
      // Step 1: Confirm the SetupIntent (verifies card, runs 3DS)
      const { error: setupError, setupIntent } = await stripe.confirmSetup({
        elements,
        confirmParams: {
          return_url: window.location.href,
        },
        redirect: "if_required",
      });

      if (setupError) {
        setError(setupError.message ?? "Card verification failed");
        return;
      }

      if (!setupIntent?.payment_method) {
        setError("Card verification failed — no payment method returned");
        return;
      }

      const paymentMethodId =
        typeof setupIntent.payment_method === "string"
          ? setupIntent.payment_method
          : setupIntent.payment_method.id;

      // Step 2: Create the org with the verified payment method
      const newOrg = await createOrganization.mutateAsync({
        name: orgName,
        slug: orgSlug,
        planTier,
        paymentMethodId,
      });

      analytics.trackEvent("organization_created", {
        organization_id: newOrg.id,
        plan_tier: planTier,
      });
      setSelectedOrganization(newOrg);
      onSuccess(newOrg);
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to create organization"));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={(e) => void handleSubmit(e)} className="contents">
      <DialogHeader>
        <DialogTitle>Set Up Payment</DialogTitle>
        <DialogDescription>
          Enter your payment details for the{" "}
          {PLAN_OPTIONS.find((p) => p.value === planTier)?.label} plan.
        </DialogDescription>
      </DialogHeader>
      <DialogBody className="space-y-4">
        <PaymentElement />
        {error && <p className="text-sm text-destructive">{error}</p>}
      </DialogBody>
      <DialogFooter>
        <Button
          type="button"
          variant="outline"
          onClick={onBack}
          disabled={isProcessing}
        >
          Back
        </Button>
        <Button type="submit" disabled={!stripe || isProcessing}>
          {isProcessing ? "Creating..." : "Create & Pay"}
        </Button>
      </DialogFooter>
    </form>
  );
}

export function CreateOrganizationModal({
  open,
  onOpenChange,
  onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated?: (org: Organization) => void;
}) {
  const [name, setName] = useState("");
  const slug = generateSlug(name.trim());
  const slugTooShort = slug.length > 0 && slug.length < 3;
  const [error, setError] = useState<string | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<PlanTier>("free");
  const [step, setStep] = useState<Step>("details");
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const createOrganization = useCreateOrganization();
  const createSetupIntent = useCreateOrgSetupIntent();
  const { setSelectedOrganization } = useOrganization();
  const analytics = useAnalytics();

  const handleDetailsSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Organization name is required");
      return;
    }

    if (slug.length < 3) {
      setError("Name must generate a slug of at least 3 characters");
      return;
    }

    if (selectedPlan === "free") {
      // Free plan: create org directly (no payment needed)
      try {
        const newOrg = await createOrganization.mutateAsync({
          name: name.trim(),
          slug,
        });
        analytics.trackEvent("organization_created", {
          organization_id: newOrg.id,
          plan_tier: "free",
        });
        setSelectedOrganization(newOrg);
        onCreated?.(newOrg);
        resetAndClose();
      } catch (err: unknown) {
        setError(getErrorMessage(err, "Failed to create organization"));
      }
    } else {
      // Paid plan: get a SetupIntent and show payment form
      try {
        const { clientSecret: secret } =
          await createSetupIntent.mutateAsync(undefined);
        setClientSecret(secret);
        setStep("payment");
      } catch (err: unknown) {
        setError(
          getErrorMessage(err, "Failed to initialize payment. Please retry."),
        );
      }
    }
  };

  const resetAndClose = () => {
    setName("");
    setError(null);
    setSelectedPlan("free");
    setStep("details");
    setClientSecret(null);
    onOpenChange(false);
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetAndClose();
    } else {
      onOpenChange(true);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        {step === "details" && (
          <form
            onSubmit={(e) => void handleDetailsSubmit(e)}
            className="contents"
          >
            <DialogHeader>
              <DialogTitle>Create Organization</DialogTitle>
              <DialogDescription>
                Create a new organization to manage your projects and team.
              </DialogDescription>
            </DialogHeader>
            <DialogBody>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="org-name">Organization Name</Label>
                  <Input
                    id="org-name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="My Organization"
                    autoFocus
                  />
                  {name.trim() && slug && (
                    <p className="text-xs text-muted-foreground">
                      Slug: <span className="font-mono">{slug}</span>
                    </p>
                  )}
                  {slugTooShort && (
                    <p className="text-sm text-destructive">
                      Slug must be at least 3 characters
                    </p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label>Plan</Label>
                  <div className="grid gap-2">
                    {PLAN_OPTIONS.map((plan) => (
                      <button
                        key={plan.value}
                        type="button"
                        onClick={() => setSelectedPlan(plan.value)}
                        className={`flex items-center gap-3 rounded-md border p-3 text-left transition-colors ${
                          selectedPlan === plan.value
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-primary/50"
                        }`}
                      >
                        <div
                          className={`h-4 w-4 rounded-full border-2 ${
                            selectedPlan === plan.value
                              ? "border-primary bg-primary"
                              : "border-muted-foreground"
                          }`}
                        />
                        <div>
                          <div className="font-medium">{plan.label}</div>
                          <div className="text-xs text-muted-foreground">
                            {plan.description}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                {error && <p className="text-sm text-destructive">{error}</p>}
              </div>
            </DialogBody>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleOpenChange(false)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  createOrganization.isPending ||
                  createSetupIntent.isPending ||
                  slugTooShort
                }
              >
                {createOrganization.isPending
                  ? "Creating..."
                  : createSetupIntent.isPending
                    ? "Loading..."
                    : selectedPlan === "free"
                      ? "Create"
                      : "Continue to Payment"}
              </Button>
            </DialogFooter>
          </form>
        )}

        {step === "payment" && clientSecret && (
          <Elements
            stripe={getStripe()}
            options={{
              clientSecret,
              appearance: stripeAppearance,
            }}
          >
            <PaymentStep
              orgName={name.trim()}
              orgSlug={slug}
              planTier={selectedPlan}
              onSuccess={(org) => {
                onCreated?.(org);
                resetAndClose();
              }}
              onBack={() => {
                setStep("details");
                setClientSecret(null);
              }}
            />
          </Elements>
        )}
      </DialogContent>
    </Dialog>
  );
}
