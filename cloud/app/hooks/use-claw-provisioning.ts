import { useQuery } from "@tanstack/react-query";
import { Effect } from "effect";
import { useEffect, useState } from "react";

import { ApiClient, eq } from "@/app/api/client";

type ProvisioningStep = {
  id: number;
  label: string;
  status: "pending" | "active" | "complete";
};

type UseClawProvisioningResult = {
  currentStep: number;
  steps: ProvisioningStep[];
  isComplete: boolean;
  isError: boolean;
  progress: number;
  errorMessage?: string;
};

export function useClawProvisioning(
  organizationId: string | null,
  clawId: string | null,
): UseClawProvisioningResult {
  const [isActive, setIsActive] = useState(false);
  const [isError, setIsError] = useState(false);

  const { data: claw, error } = useQuery({
    ...eq.queryOptions({
      queryKey: ["claws", organizationId, clawId, "provisioning"],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.claws.get({
            path: {
              organizationId: organizationId!,
              clawId: clawId!,
            },
          });
        }),
    }),
    enabled: !!organizationId && !!clawId && !isActive && !isError,
    refetchInterval: 2500,
  });

  const [currentStep, setCurrentStep] = useState(0);
  const [stepStartTimes, setStepStartTimes] = useState<Record<number, number>>(
    {},
  );
  const [errorMessage, setErrorMessage] = useState<string | undefined>();

  // Define the 6 steps
  const stepLabels = [
    "Creating identity",
    "Provisioning storage",
    "Encrypting credentials",
    "Starting container",
    "Warming up",
    "Ready",
  ];

  // Track when we've seen the API return (step 1 completes)
  useEffect(() => {
    if (claw && currentStep === 0) {
      setCurrentStep(1);
      setStepStartTimes((prev) => ({ ...prev, 1: Date.now() }));
    }
  }, [claw, currentStep]);

  // Stop polling once active
  useEffect(() => {
    if (claw?.status === "active") {
      setIsActive(true);
    }
  }, [claw?.status]);

  // Handle error status or query error
  useEffect(() => {
    if (error) {
      setIsError(true);
      setErrorMessage("Failed to fetch claw status");
    }
    if (claw?.status === "error") {
      setIsError(true);
      setErrorMessage(claw.lastError ?? "Provisioning failed");
    }
  }, [claw, error]);

  // Handle timeout (60s)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (currentStep < 5) {
        setIsError(true);
        setErrorMessage("Provisioning timed out");
      }
    }, 60000);

    return () => clearTimeout(timeoutId);
  }, [currentStep]);

  // Time-interpolation: advance steps every 2s if still in provisioning
  useEffect(() => {
    if (currentStep >= 1 && currentStep < 4 && claw?.status !== "active") {
      const stepStart = stepStartTimes[currentStep];
      if (!stepStart) {
        setStepStartTimes((prev) => ({ ...prev, [currentStep]: Date.now() }));
        return;
      }

      const elapsed = Date.now() - stepStart;
      if (elapsed >= 2000) {
        setCurrentStep((prev) => prev + 1);
        setStepStartTimes((prev) => ({
          ...prev,
          [currentStep + 1]: Date.now(),
        }));
      } else {
        // Check again in remaining time
        const timeoutId = setTimeout(() => {
          setCurrentStep((prev) => prev + 1);
          setStepStartTimes((prev) => ({
            ...prev,
            [currentStep + 1]: Date.now(),
          }));
        }, 2000 - elapsed);
        return () => clearTimeout(timeoutId);
      }
    }
  }, [currentStep, claw?.status, stepStartTimes]);

  // Fast-forward if API returns active before all steps shown
  useEffect(() => {
    if (claw?.status === "active" && currentStep < 5) {
      const fastForwardInterval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= 5) {
            clearInterval(fastForwardInterval);
            return prev;
          }
          return prev + 1;
        });
      }, 200);

      return () => clearInterval(fastForwardInterval);
    }
  }, [claw?.status]); // Only depend on status change, not currentStep

  // Generate steps array
  const steps: ProvisioningStep[] = stepLabels.map((label, index) => ({
    id: index,
    label,
    status:
      index < currentStep
        ? "complete"
        : index === currentStep
          ? "active"
          : "pending",
  }));

  // Calculate progress (0-100)
  let progress = 0;
  if (claw?.status === "active" && currentStep >= 5) {
    progress = 100;
  } else {
    // Base progress from completed steps
    const baseProgress = (currentStep / 6) * 100;

    // Add interpolated progress for current step
    const stepStart = stepStartTimes[currentStep];
    if (stepStart && currentStep < 4) {
      const elapsed = Date.now() - stepStart;
      const stepProgress = Math.min(elapsed / 2000, 0.99); // Never reach 100% until truly done
      progress = baseProgress + (stepProgress * 100) / 6;
    } else if (currentStep === 4 && claw?.status !== "active") {
      // Step 4 (Warming up) - slow down if taking longer than expected
      const stepStart = stepStartTimes[4];
      if (stepStart) {
        const elapsed = Date.now() - stepStart;
        // Logarithmic slowdown
        const stepProgress = Math.min(
          0.5 + Math.log10(elapsed / 1000) / 10,
          0.99,
        );
        progress = baseProgress + (stepProgress * 100) / 6;
      } else {
        progress = baseProgress;
      }
    } else {
      progress = baseProgress;
    }
  }

  const isComplete = claw?.status === "active" && currentStep >= 5;

  return {
    currentStep,
    steps,
    isComplete,
    isError,
    progress: Math.min(Math.round(progress), 100),
    errorMessage,
  };
}
