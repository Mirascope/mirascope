import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/app/contexts/auth";
import { useAcceptInvitation } from "@/app/api/organization-invitations";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Alert, AlertDescription } from "@/app/components/ui/alert";
import { Loader2, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

export const Route = createFileRoute("/invitations/accept")({
  component: AcceptInvitationPage,
});

type AcceptState = "idle" | "accepting" | "success" | "error";

function AcceptInvitationPage() {
  // Extract token from URL query params
  const searchParams = new URLSearchParams(window.location.search);
  const token = searchParams.get("token") || "";
  const { user } = useAuth();
  const navigate = useNavigate();
  const acceptInvitation = useAcceptInvitation();
  const [state, setState] = useState<AcceptState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleAccept = useCallback(async () => {
    if (!token) {
      setErrorMessage("Invalid invitation link - no token provided");
      setState("error");
      return;
    }

    setState("accepting");
    setErrorMessage(null);

    try {
      const result = await acceptInvitation.mutateAsync(token);
      setState("success");

      // Store the organization ID so it gets selected on dashboard
      localStorage.setItem(
        "mirascope:selectedOrganizationId",
        result.organizationId,
      );

      // Redirect to cloud dashboard after short delay
      setTimeout(() => {
        void navigate({ to: "/cloud/dashboard" });
      }, 2000);
    } catch (error) {
      setState("error");
      if (error instanceof Error) {
        // Parse common error messages
        const message = error.message.toLowerCase();
        if (message.includes("expired")) {
          setErrorMessage("This invitation has expired");
        } else if (message.includes("already") || message.includes("used")) {
          setErrorMessage("This invitation has already been used");
        } else if (message.includes("not found")) {
          setErrorMessage("Invalid invitation link");
        } else if (message.includes("email")) {
          setErrorMessage(
            "This invitation was sent to a different email address",
          );
        } else {
          setErrorMessage(error.message);
        }
      } else {
        setErrorMessage("Failed to accept invitation");
      }
    }
  }, [token, acceptInvitation, navigate]);

  // Auto-accept if user is logged in
  useEffect(() => {
    if (user && token && state === "idle") {
      void handleAccept();
    }
  }, [user, token, state, handleAccept]);

  if (!user) {
    // Store the current URL with token for redirect after login
    const handleSignIn = () => {
      const redirectUrl = `/invitations/accept?token=${token}`;
      sessionStorage.setItem("redirectAfterLogin", redirectUrl);
      void navigate({ to: "/cloud" });
    };

    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Sign in to accept invitation</CardTitle>
            <CardDescription>
              You need to be signed in to accept this invitation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={handleSignIn} className="w-full">
              Sign In
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-red-500" />
              <CardTitle>Invalid Invitation</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              This invitation link is invalid or malformed.
            </p>
            <Button
              onClick={() => void navigate({ to: "/organizations" })}
              className="mt-4 w-full"
              variant="outline"
            >
              Go to Organizations
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        {state === "accepting" && (
          <>
            <CardHeader>
              <CardTitle>Accepting Invitation</CardTitle>
              <CardDescription>
                Please wait while we process your invitation
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center py-8">
              <Loader2 className="h-12 w-12 animate-spin text-muted-foreground" />
            </CardContent>
          </>
        )}

        {state === "success" && (
          <>
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <CardTitle>Invitation Accepted!</CardTitle>
              </div>
              <CardDescription>
                You've successfully joined the organization
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Alert className="border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
                <AlertDescription className="text-green-800 dark:text-green-200">
                  Redirecting you to your dashboard...
                </AlertDescription>
              </Alert>
            </CardContent>
          </>
        )}

        {state === "error" && (
          <>
            <CardHeader>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-500" />
                <CardTitle>Unable to Accept Invitation</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="destructive">
                <AlertDescription>
                  {errorMessage || "An unexpected error occurred"}
                </AlertDescription>
              </Alert>
              <Button
                onClick={() => void navigate({ to: "/organizations" })}
                className="w-full"
                variant="outline"
              >
                Go to Organizations
              </Button>
            </CardContent>
          </>
        )}

        {state === "idle" && (
          <>
            <CardHeader>
              <CardTitle>Accept Invitation</CardTitle>
              <CardDescription>
                Click below to accept your organization invitation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => void handleAccept()} className="w-full">
                Accept Invitation
              </Button>
            </CardContent>
          </>
        )}
      </Card>
    </div>
  );
}
