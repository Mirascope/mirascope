import { Check, Circle, Loader2, X } from "lucide-react";
import { useEffect, useState } from "react";

import type { Claw } from "@/api/claws.schemas";

import { Button } from "@/app/components/ui/button";
import { useClawProvisioning } from "@/app/hooks/use-claw-provisioning";
import { cn } from "@/app/lib/utils";

export function ClawProvisioningView({
  claw,
  onComplete,
  onSkip,
  onRetry,
}: {
  claw: Claw;
  onComplete: () => void;
  onSkip: () => void;
  onRetry?: () => void;
}) {
  const { steps, isComplete, isError, progress, errorMessage } =
    useClawProvisioning(claw.organizationId, claw.id);

  const [showComplete, setShowComplete] = useState(false);

  // Handle completion animation
  useEffect(() => {
    if (isComplete) {
      setShowComplete(true);
      const timer = setTimeout(() => {
        onComplete();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [isComplete, onComplete]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-1">
        <h2 className="text-lg font-semibold">
          {isError
            ? "Provisioning Failed"
            : isComplete
              ? "Your Claw is Ready!"
              : "Setting Up Your Claw"}
        </h2>
        <div className="space-y-0.5">
          <p className="text-sm font-medium">{claw.displayName ?? claw.slug}</p>
          <p className="text-xs text-muted-foreground font-mono">{claw.slug}</p>
        </div>
      </div>

      {isError ? (
        /* Error State */
        <div className="space-y-4">
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <X className="h-8 w-8 text-destructive mx-auto mb-2" />
            <p className="text-sm text-destructive">
              {errorMessage ?? "An error occurred during provisioning"}
            </p>
          </div>
          <div className="flex gap-2 justify-center">
            {onRetry && (
              <Button onClick={onRetry} variant="default">
                Retry
              </Button>
            )}
            <Button onClick={onSkip} variant="outline">
              Go to Claw Page
            </Button>
          </div>
        </div>
      ) : (
        /* Normal Flow */
        <>
          {/* Vertical Stepper */}
          <div className="space-y-0">
            {steps.map((step, index) => (
              <div key={step.id} className="flex gap-3 items-start">
                {/* Icon Column */}
                <div className="flex flex-col items-center pt-0.5">
                  <div
                    className={cn(
                      "flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300",
                      step.status === "complete" &&
                        "bg-primary border-primary text-primary-foreground",
                      step.status === "active" &&
                        "border-primary text-primary animate-pulse",
                      step.status === "pending" &&
                        "border-muted-foreground/30 text-muted-foreground/30",
                      showComplete && "animate-[glow_0.5s_ease-in-out]",
                    )}
                  >
                    {step.status === "complete" ? (
                      <Check className="h-4 w-4" />
                    ) : step.status === "active" ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Circle className="h-3 w-3 fill-current" />
                    )}
                  </div>
                  {/* Connecting Line */}
                  {index < steps.length - 1 && (
                    <div
                      className={cn(
                        "w-0.5 h-8 transition-all duration-500 ease-out",
                        step.status === "complete"
                          ? "bg-primary"
                          : "bg-muted-foreground/20",
                      )}
                    />
                  )}
                </div>
                {/* Label Column */}
                <div className="pt-1 pb-4">
                  <p
                    className={cn(
                      "text-sm font-medium transition-colors duration-300",
                      step.status === "complete" && "text-foreground",
                      step.status === "active" && "text-primary",
                      step.status === "pending" && "text-muted-foreground/50",
                    )}
                  >
                    {step.label}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Progress Bars (WiFi/Cell Signal Style) */}
          <div className="flex items-end justify-center gap-1.5 h-12">
            {[20, 35, 50, 65, 80].map((height, index) => {
              const barProgress = Math.max(0, progress - index * 20);
              const fillPercent = Math.min(barProgress / 20, 1) * 100;

              return (
                <div
                  key={index}
                  className="relative w-8 bg-muted-foreground/10 rounded-t-sm"
                  style={{ height: `${height}%` }}
                >
                  <div
                    className={cn(
                      "absolute bottom-0 w-full rounded-t-sm transition-all duration-500 ease-out",
                      showComplete
                        ? "bg-primary animate-[glow_0.5s_ease-in-out]"
                        : "bg-primary",
                    )}
                    style={{ height: `${fillPercent}%` }}
                  />
                </div>
              );
            })}
          </div>

          {/* Skip Button */}
          <div className="text-center">
            <Button
              onClick={onSkip}
              variant="ghost"
              size="sm"
              className="text-muted-foreground"
            >
              Skip to Claw Page
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
