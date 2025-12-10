import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";
// Import from shared config file
import type { Provider } from "@/src/config/providers";
import { providers, providerDefaults } from "@/src/config/providers";

// Re-export these for backward compatibility
export type { Provider };
export { providers, providerDefaults };

import { temporarilyEnableSyncHighlighting } from "@/mirascope-ui/lib/code-highlight";

// Create a context to share the selected provider
interface ProviderContextType {
  provider: Provider;
  setProvider: (provider: Provider) => void;
  providerInfo: {
    displayName: string;
    defaultModel: string;
  };
}

const ProviderContext = createContext<ProviderContextType | undefined>(undefined);

// Helper function to validate a provider string
const validateProvider = (provider: string | null, defaultFallback: Provider): Provider => {
  if (!provider || !providers.includes(provider as Provider)) {
    return defaultFallback; // Default fallback if invalid
  }
  return provider as Provider;
};

// Provider component that wraps the content and provides the state
export function ProviderContextProvider({
  children,
  defaultProvider = "openai",
  onProviderChange,
}: {
  children: ReactNode;
  defaultProvider?: Provider;
  onProviderChange?: (provider: Provider) => void;
}) {
  // Initialize Provider from localStorage if available
  const [provider, setProvider] = useState<Provider>(() => {
    if (typeof window !== "undefined") {
      const savedProvider = localStorage.getItem("selectedProvider");
      return validateProvider(savedProvider, defaultProvider);
    }
    return defaultProvider;
  });

  // Create a wrapper for setProvider that calls the callback and updates localStorage
  const handleProviderChange = (newProvider: Provider) => {
    temporarilyEnableSyncHighlighting();
    setProvider(newProvider);

    // Save to localStorage
    if (typeof window !== "undefined") {
      localStorage.setItem("selectedProvider", newProvider);
    }

    // Call external callback if provided
    if (onProviderChange) {
      onProviderChange(newProvider);
    }
  };

  // Get the provider info
  const providerInfo = providerDefaults[provider];

  return (
    <ProviderContext.Provider
      value={{
        provider,
        setProvider: handleProviderChange,
        providerInfo,
      }}
    >
      {children}
    </ProviderContext.Provider>
  );
}

// Default provider to use when outside of ProviderContextProvider
const defaultProvider: Provider = "openai";

// Hook to access the provider context
export function useProvider() {
  const context = useContext(ProviderContext);
  if (context === undefined) {
    // Return a default context when no provider is available
    // This happens in blog posts or other areas without the provider dropdown
    return {
      provider: defaultProvider,
      setProvider: () => {
        console.warn("Attempted to set provider outside of ProviderContextProvider");
      },
      providerInfo: providerDefaults[defaultProvider],
    };
  }
  return context;
}
