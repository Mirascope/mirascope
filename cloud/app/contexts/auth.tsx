import { useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { createContext, useContext, useEffect, type ReactNode } from "react";

import type { PublicUser } from "@/db/schema";

import { useAuthStatus, useLogout } from "@/app/api/auth";
import { useAnalytics } from "@/app/contexts/analytics";

type AuthContextType = {
  user: PublicUser | null;
  isLoading: boolean;
  loginWithGitHub: () => void;
  loginWithGoogle: () => void;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const analytics = useAnalytics();

  const { data: user, isLoading } = useAuthStatus();
  const logoutMutation = useLogout();

  // Track successful login/signup and identify user
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get("success");

    if (success === "true") {
      void queryClient.invalidateQueries({ queryKey: ["auth", "me"] });

      const provider = urlParams.get("provider") || "unknown";
      const isNewUser = urlParams.get("new_user") === "true";

      if (isNewUser) {
        analytics.trackEvent("sign_up", { provider });
      } else {
        analytics.trackEvent("user_login", { provider });
      }

      window.history.replaceState({}, document.title, window.location.pathname);

      // Check if there's a redirect URL stored (e.g., from invitation acceptance)
      const redirectUrl = sessionStorage.getItem("redirectAfterLogin");
      if (redirectUrl) {
        sessionStorage.removeItem("redirectAfterLogin");
        window.location.href = redirectUrl;
      } else if (isNewUser) {
        // New users go through onboarding
        void navigate({ to: "/cloud/onboarding", replace: true });
      } else {
        void navigate({ to: "/cloud", replace: true });
      }
    }
  }, [navigate, queryClient, analytics]);

  // Identify user when user data becomes available
  useEffect(() => {
    if (user && !isLoading) {
      analytics.identify(user.id, {
        email: user.email,
        name: user.name,
      });
    }
  }, [user, isLoading, analytics]);

  const loginWithGitHub = () => {
    window.location.href = "/auth/github";
  };

  const loginWithGoogle = () => {
    window.location.href = "/auth/google";
  };

  const handleLogout = async () => {
    try {
      analytics.trackEvent("user_logout");
      await logoutMutation.mutateAsync();
    } catch (error) {
      if (process.env.NODE_ENV === "development") {
        console.error("Logout failed:", error);
      }
    }
  };

  const value = {
    user: user ?? null,
    isLoading,
    loginWithGitHub,
    loginWithGoogle,
    logout: handleLogout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
