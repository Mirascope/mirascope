import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { ArrowRight, Check, Info, Loader2 } from "lucide-react";
import { useState, useEffect, type FormEvent } from "react";

import {
  useCompleteOnboarding,
  type OnboardingResponse,
} from "@/app/api/onboarding";
import { Protected } from "@/app/components/protected";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { useAnalytics } from "@/app/contexts/analytics";
import { useClaw } from "@/app/contexts/claw";
import { useOrganization } from "@/app/contexts/organization";
import {
  useOnboarding,
  generateDefaultOrgName,
} from "@/app/hooks/use-onboarding";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

type Step = "org" | "claw" | "done";

function OnboardingContent() {
  const navigate = useNavigate();
  const { needsOnboarding, isLoadingOrgs, completeOnboarding } =
    useOnboarding();
  const { setSelectedOrganization } = useOrganization();
  const { setSelectedClaw } = useClaw();
  const completeOnboardingMutation = useCompleteOnboarding();
  const analytics = useAnalytics();

  const [step, setStep] = useState<Step>("org");
  const [organizationName, setOrganizationName] = useState(() =>
    generateDefaultOrgName(),
  );
  const [clawName, setClawName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [onboardingResult, setOnboardingResult] =
    useState<OnboardingResponse | null>(null);
  // Track if we've started onboarding to prevent redirect after org creation
  const [hasStartedOnboarding, setHasStartedOnboarding] = useState(false);

  // Redirect to dashboard if user already has organizations (doesn't need onboarding)
  // But don't redirect if we're in the middle of onboarding (hasStartedOnboarding)
  useEffect(() => {
    if (!isLoadingOrgs && !needsOnboarding && !hasStartedOnboarding) {
      void navigate({ to: "/cloud", replace: true });
    }
  }, [isLoadingOrgs, needsOnboarding, hasStartedOnboarding, navigate]);

  const handleOrgSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!organizationName.trim()) {
      setError("Organization name is required");
      return;
    }

    setHasStartedOnboarding(true);
    setStep("claw");
  };

  const handleClawSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!clawName.trim()) {
      setError("Claw name is required");
      return;
    }

    try {
      const result = await completeOnboardingMutation.mutateAsync({
        organizationName: organizationName.trim(),
        clawName: clawName.trim(),
      });

      // Update contexts with newly created resources
      setSelectedOrganization(result.organization);
      setSelectedClaw(result.claw);

      // Track onboarding completion
      analytics.trackEvent("onboarding_completed", {
        organization_id: result.organization.id,
        claw_id: result.claw.id,
      });

      // Store result and move to done step
      setOnboardingResult(result);
      setStep("done");
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to complete onboarding"));
    }
  };

  const handleGoToDashboard = () => {
    completeOnboarding();
    void navigate({ to: "/cloud", replace: true });
  };

  // Show loading state while checking if onboarding is needed
  if (isLoadingOrgs) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <div className="w-full max-w-lg">
        {step === "org" && (
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Welcome to Mirascope</CardTitle>
              <CardDescription>
                Let's set up your organization to get started.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => void handleOrgSubmit(e)}
                className="space-y-6"
              >
                <div className="space-y-2">
                  <Label htmlFor="org-name">Organization Name</Label>
                  <Input
                    id="org-name"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    placeholder="My Organization"
                    autoFocus
                  />
                  <p className="text-sm text-muted-foreground">
                    Slug:{" "}
                    <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                      {generateSlug(organizationName) || "..."}
                    </code>
                  </p>
                  {error && <p className="text-sm text-destructive">{error}</p>}
                </div>

                <Button type="submit" className="w-full">
                  Next
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {step === "claw" && (
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Create Your First Claw</CardTitle>
              <CardDescription>
                A claw is an AI agent you can deploy and manage.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => void handleClawSubmit(e)}
                className="space-y-6"
              >
                <div className="space-y-2">
                  <Label htmlFor="claw-name">Claw Name</Label>
                  <Input
                    id="claw-name"
                    value={clawName}
                    onChange={(e) => setClawName(e.target.value)}
                    placeholder="My First Claw"
                    autoFocus
                  />
                  <p className="text-sm text-muted-foreground">
                    Slug:{" "}
                    <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                      {generateSlug(clawName) || "..."}
                    </code>
                  </p>
                  {error && <p className="text-sm text-destructive">{error}</p>}
                </div>

                <div className="flex items-start gap-3 rounded-lg border border-border bg-muted/50 p-4">
                  <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Creating a claw automatically sets up its home project,
                    environment, and API key so it's ready to deploy.
                  </p>
                </div>

                <Button
                  type="submit"
                  className="w-full"
                  disabled={completeOnboardingMutation.isPending}
                >
                  {completeOnboardingMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {step === "done" && onboardingResult && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <CardTitle className="text-2xl">You're All Set!</CardTitle>
              <CardDescription>
                Your organization{" "}
                <strong>{onboardingResult.organization.name}</strong> and claw{" "}
                <strong>{onboardingResult.claw.displayName}</strong> are ready.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Credits Info Section */}
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950">
                <h3 className="font-semibold text-blue-800 dark:text-blue-200">
                  Earn Up to $30 in Credits
                </h3>
                <p className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                  We're offering free credits to early adopters who help us
                  build a better product. To learn about current opportunities,
                  join our Discord and send William Bakst a DM — we'd love to
                  hear what you're building and share how you can earn credits.
                </p>
                <a
                  href="https://mirascope.com/discord-invite"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-3 inline-block text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
                >
                  Join our Discord →
                </a>
              </div>

              <Button onClick={handleGoToDashboard} className="w-full">
                Go to Dashboard
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

function OnboardingPage() {
  return (
    <Protected>
      <OnboardingContent />
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/projects/onboarding")({
  component: OnboardingPage,
});
