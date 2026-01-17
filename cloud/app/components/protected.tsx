import { useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/app/contexts/auth";
import { useEffect } from "react";
import type { ReactNode } from "react";

export function Protected({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Only redirect on client-side after auth check completes
    if (!isLoading && !user) {
      void navigate({ to: "/cloud/login", replace: true });
    }
  }, [user, isLoading, navigate]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    // Show loading while redirect happens
    return <div>Loading...</div>;
  }

  return <>{children}</>;
}
