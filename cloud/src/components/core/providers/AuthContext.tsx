import { useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, type ReactNode } from "react";
import type { PublicUser } from "@/db/schema";
import { useAuthStatus, useLogout } from "@/src/api/auth";

type AuthContextType = {
  user: PublicUser | null;
  isLoading: boolean;
  loginWithGitHub: () => void;
  loginWithGoogle: () => void;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useAuthStatus();
  const logoutMutation = useLogout();

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const success = urlParams.get("success");

    if (success === "true") {
      void queryClient.invalidateQueries({ queryKey: ["auth", "me"] });

      window.history.replaceState({}, document.title, window.location.pathname);

      void navigate({ to: "/", replace: true });
    }
  }, [navigate, queryClient]);

  const loginWithGitHub = () => {
    window.location.href = "/auth/github";
  };

  const loginWithGoogle = () => {
    window.location.href = "/auth/google";
  };

  const handleLogout = async () => {
    try {
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
