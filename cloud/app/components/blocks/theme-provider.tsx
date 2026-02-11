import { useRouterState } from "@tanstack/react-router";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type Theme = "light" | "dark" | "system";
export type ViewMode = "human" | "machine";

// Simple theme API interface
interface ThemeAPI {
  // Current theme preference (light/dark/system)
  theme: Theme;
  // Actual theme being displayed (light/dark)
  current: "light" | "dark";
  // Set specific theme
  set: (theme: Theme) => void;
  // Current view mode (human/machine)
  viewMode: ViewMode;
  // Set view mode
  setViewMode: (mode: ViewMode) => void;
  // Whether the current page is the landing page
  isLandingPage: boolean;
  // Whether the current page is the login page
  isLoginPage: boolean;
  // Whether the current page is the router waitlist page
  isRouterWaitlistPage: boolean;
}

// Create the context with default values
const ThemeContext = createContext<ThemeAPI>({
  theme: "system",
  current: "light",
  set: () => {},
  viewMode: "human",
  setViewMode: () => {},
  isLandingPage: false,
  isLoginPage: false,
  isRouterWaitlistPage: false,
});

// Hook for components to use the theme
export function useTheme() {
  return useContext(ThemeContext);
}

// Hook specifically for view mode
export function useViewMode() {
  return useContext(ThemeContext).viewMode;
}

// Hook specifically for landing page status
export function useIsLandingPage() {
  return useContext(ThemeContext).isLandingPage;
}

// Hook specifically for login page status
export function useIsLoginPage() {
  return useContext(ThemeContext).isLoginPage;
}

// Hook specifically for router waitlist page status
export function useIsRouterWaitlistPage() {
  return useContext(ThemeContext).isRouterWaitlistPage;
}

// Get stored theme preference from localStorage
function getStoredTheme(): Theme {
  if (typeof window === "undefined") return "system";
  return (localStorage.getItem("theme") as Theme) || "system";
}

// Get stored view mode preference from localStorage
function getStoredViewMode(): ViewMode {
  if (typeof window === "undefined") return "human";
  return (localStorage.getItem("viewMode") as ViewMode) || "human";
}

// Determine effective theme based on preference and system settings
function getEffectiveTheme(theme: Theme): "light" | "dark" {
  if (theme !== "system") return theme;
  if (typeof window === "undefined") return "light";
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

// Apply theme to document
function applyTheme(theme: "light" | "dark"): void {
  if (typeof document === "undefined") return;

  const root = document.documentElement;
  root.classList.remove("light", "dark");
  root.classList.add(theme);
}

interface ThemeProviderProps {
  children: ReactNode;
}

// Main theme provider for the application
export function ThemeProvider({ children }: ThemeProviderProps) {
  // Theme preference (light/dark/system)
  const [theme, setTheme] = useState<Theme>("system");
  // Actual theme being applied (light/dark)
  const [current, setCurrent] = useState<"light" | "dark">("light");
  // View mode (human/machine)
  const [viewMode, setViewMode] = useState<ViewMode>("human");
  // Track if client-side code has run
  const [isHydrated, setIsHydrated] = useState(false);

  // Get router to determine if we're on the landing page or router waitlist page
  const router = useRouterState();
  const isLandingPage = router.location.pathname === "/";
  const isLoginPage = router.location.pathname === "/login";
  const isRouterWaitlistPage = router.location.pathname === "/router-waitlist";

  // Initialize theme and view mode on mount
  useEffect(() => {
    const savedTheme = getStoredTheme();
    const effectiveTheme = getEffectiveTheme(savedTheme);
    const savedViewMode = getStoredViewMode();

    setTheme(savedTheme);
    setCurrent(effectiveTheme);
    setViewMode(savedViewMode);
    applyTheme(effectiveTheme);
    setIsHydrated(true);
  }, []);

  // Listen for system theme changes
  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleChange = () => {
      if (theme === "system") {
        const newTheme = getEffectiveTheme("system");
        setCurrent(newTheme);
        applyTheme(newTheme);
      }
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [theme]);

  // Update theme handler
  const setThemeHandler = (newTheme: Theme) => {
    const effectiveTheme = getEffectiveTheme(newTheme);

    // Update state
    setTheme(newTheme);
    setCurrent(effectiveTheme);

    // Apply to DOM
    applyTheme(effectiveTheme);

    // Store preference
    if (typeof window !== "undefined") {
      localStorage.setItem("theme", newTheme);
    }
  };

  // Update view mode handler
  const setViewModeHandler = (newViewMode: ViewMode) => {
    setViewMode(newViewMode);

    // Store preference
    if (typeof window !== "undefined") {
      localStorage.setItem("viewMode", newViewMode);
    }
  };

  // Add the home-page class to the HTML element
  if (isHydrated && typeof document !== "undefined") {
    if (isLandingPage || isLoginPage || isRouterWaitlistPage) {
      document.documentElement.classList.add("home-page");
    } else {
      document.documentElement.classList.remove("home-page");
    }
  }

  // Always render ThemeContext.Provider to avoid unmounting/remounting children
  // when isHydrated changes from false to true
  return (
    <ThemeContext.Provider
      value={{
        theme,
        current,
        set: setThemeHandler,
        viewMode,
        setViewMode: setViewModeHandler,
        isLandingPage,
        isLoginPage,
        isRouterWaitlistPage,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

// Provider for Storybook usage
interface StorybookThemeProviderProps {
  children: ReactNode;
  initialTheme?: Theme;
  initialCurrent?: "light" | "dark";
  initialViewMode?: ViewMode;
  isLandingPage?: boolean;
  isLoginPage?: boolean;
  isRouterWaitlistPage?: boolean;
}

/**
 * A simplified theme provider for Storybook
 *
 * This provider doesn't manipulate the document directly as that doesn't
 * work well with Storybook's iframe-based component rendering. Instead,
 * we just provide the theme context and let ProductThemeDecorator handle
 * the DOM elements and styling.
 */
export function StorybookThemeProvider({
  children,
  initialTheme = "system",
  initialCurrent = "light",
  initialViewMode = "human",
  isLandingPage = false,
  isLoginPage = false,
  isRouterWaitlistPage = false,
}: StorybookThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const [current, setCurrent] = useState<"light" | "dark">(initialCurrent);
  const [viewMode, setViewMode] = useState<ViewMode>(initialViewMode);

  // Theme switching handler - just update state
  const setThemeHandler = (newTheme: Theme) => {
    setTheme(newTheme);

    // In Storybook, we honor the requested theme directly rather than using system settings
    if (newTheme === "system") {
      // For "system" in Storybook, we keep the current theme
      return;
    }

    // Update the current theme
    setCurrent(newTheme);
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        current,
        set: setThemeHandler,
        viewMode,
        setViewMode,
        isLandingPage,
        isLoginPage,
        isRouterWaitlistPage,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}
