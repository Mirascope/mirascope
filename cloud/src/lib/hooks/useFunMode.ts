import { useContext } from "react";
import { FunModeContext } from "@/src/components";

/**
 * Custom hook to access fun mode state from context
 *
 * @returns [funMode, toggleFunMode] - Current state and toggle function
 */
export function useFunMode(): [boolean, () => void] {
  const context = useContext(FunModeContext);
  if (!context) {
    throw new Error("useFunMode must be used within a FunModeProvider");
  }

  return [context.funMode, context.toggleFunMode];
}

export default useFunMode;
