import { useNavigate } from "@tanstack/react-router";
import { useAuth } from "@/src/components/core/providers/AuthContext";
import { useEffect } from "react";
import type { ReactNode } from "react";

function Protected({ children }: { children: ReactNode }) {
  const { user, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Only redirect on client-side after auth check completes
    if (!isLoading && !user) {
      void navigate({ to: "/login", replace: true });
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

export default Protected;
