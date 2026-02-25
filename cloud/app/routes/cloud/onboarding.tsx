import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Check, Loader2 } from "lucide-react";
import { useState, useEffect, type FormEvent } from "react";

import {
  useCompleteOnboarding,
  type OnboardingResponse,
} from "@/app/api/onboarding";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
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
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import {
  useOnboarding,
  generateDefaultOrgName,
} from "@/app/hooks/use-onboarding";
import { getErrorMessage } from "@/app/lib/errors";
import { generateSlug } from "@/db/slug";

type Step = "setup" | "success";

const PYTHON_CODE_EXAMPLE = `import os

from mirascope import llm

os.environ["MIRASCOPE_API_KEY"] = "YOUR_API_KEY"

# Register Mirascope Router for all providers
llm.register_provider(
    "mirascope",
    scope=["anthropic/", "google/", "openai/"],
)


@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)`;

function OnboardingContent() {
  const navigate = useNavigate();
  const { needsOnboarding, isLoadingOrgs, completeOnboarding } =
    useOnboarding();
  const { setSelectedOrganization } = useOrganization();
  const { setSelectedProject } = useProject();
  const { setSelectedEnvironment } = useEnvironment();
  const completeOnboardingMutation = useCompleteOnboarding();
  const analytics = useAnalytics();

  const [step, setStep] = useState<Step>("setup");
  const [organizationName, setOrganizationName] = useState(() =>
    generateDefaultOrgName(),
  );
  const [error, setError] = useState<string | null>(null);
  const [onboardingResult, setOnboardingResult] =
    useState<OnboardingResponse | null>(null);
  // Track if we've started onboarding to prevent redirect after org creation
  const [hasStartedOnboarding, setHasStartedOnboarding] = useState(false);

  // Redirect to dashboard if user already has organizations (doesn't need onboarding)
  // But don't redirect if we're in the middle of onboarding (hasStartedOnboarding)
  useEffect(() => {
    if (!isLoadingOrgs && !needsOnboarding && !hasStartedOnboarding) {
      void navigate({ to: "/cloud/dashboard", replace: true });
    }
  }, [isLoadingOrgs, needsOnboarding, hasStartedOnboarding, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!organizationName.trim()) {
      setError("Organization name is required");
      return;
    }

    // Mark that we've started onboarding to prevent auto-redirect
    setHasStartedOnboarding(true);

    try {
      const result = await completeOnboardingMutation.mutateAsync({
        organizationName: organizationName.trim(),
      });

      // Update contexts with newly created resources
      setSelectedOrganization(result.organization);
      setSelectedProject(result.project);
      setSelectedEnvironment(result.environment);

      // Track onboarding completion
      analytics.trackEvent("onboarding_completed", {
        organization_id: result.organization.id,
        project_id: result.project.id,
        environment_id: result.environment.id,
      });

      // Store result and move to success step
      setOnboardingResult(result);
      setStep("success");
    } catch (err: unknown) {
      setError(getErrorMessage(err, "Failed to complete onboarding"));
    }
  };

  const handleGoToDashboard = () => {
    completeOnboarding();
    void navigate({ to: "/cloud/dashboard", replace: true });
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
        {step === "setup" && (
          <Card>
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Welcome to Mirascope</CardTitle>
              <CardDescription>
                Let's set up your organization to get started.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form
                onSubmit={(e) => void handleSubmit(e)}
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

                <div className="rounded-lg border border-border bg-muted/50 p-4">
                  <p className="text-sm text-muted-foreground">
                    We'll create a <strong>Default</strong> project and
                    environment, plus generate your first API key so you can
                    start building right away.
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
                    "Create Workspace"
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {step === "success" && onboardingResult && (
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900">
                <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <CardTitle className="text-2xl">You're All Set!</CardTitle>
              <CardDescription>
                Your workspace{" "}
                <strong>{onboardingResult.organization.name}</strong> is ready.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* API Key Section */}
              <div className="space-y-2">
                <Label>Your API Key</Label>
                <CodeBlock
                  code={onboardingResult.apiKey.key}
                  language="text"
                  showLineNumbers={false}
                />
                <p className="text-sm text-amber-600 dark:text-amber-400">
                  Copy this key now — you won't be able to see it again.
                </p>
              </div>

              {/* Code Example Section */}
              <div className="space-y-2">
                <Label>Quick Start</Label>
                <CodeBlock
                  code={PYTHON_CODE_EXAMPLE.replace(
                    "YOUR_API_KEY",
                    onboardingResult.apiKey.key,
                  )}
                  language="python"
                  showLineNumbers={false}
                />
              </div>

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

export const Route = createFileRoute("/cloud/onboarding")({
  component: OnboardingPage,
});
