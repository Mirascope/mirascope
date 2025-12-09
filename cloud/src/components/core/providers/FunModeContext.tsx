import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";

interface FunModeContextType {
  funMode: boolean;
  toggleFunMode: () => void;
}

export const FunModeContext = createContext<FunModeContextType | undefined>(undefined);

export function FunModeProvider({ children }: { children: ReactNode }) {
  // Initialize state but update after mount to avoid hydration mismatch
  const [funMode, setFunMode] = useState<boolean>(false);

  // Load from localStorage on mount
  useEffect(() => {
    if (typeof window !== "undefined") {
      setFunMode(localStorage.getItem("funMode") === "true");
    }
  }, []);

  // Toggle fun mode and update localStorage
  const toggleFunMode = () => {
    const newMode = !funMode;
    setFunMode(newMode);

    if (typeof window !== "undefined") {
      localStorage.setItem("funMode", newMode.toString());
    }
  };

  return (
    <FunModeContext.Provider
      value={{
        funMode,
        toggleFunMode,
      }}
    >
      {children}
    </FunModeContext.Provider>
  );
}

// Hook to access the fun mode context
export function useFunMode(): [boolean, () => void] {
  const context = useContext(FunModeContext);
  if (context === undefined) {
    throw new Error("useFunMode must be used within a FunModeProvider");
  }
  return [context.funMode, context.toggleFunMode];
}
