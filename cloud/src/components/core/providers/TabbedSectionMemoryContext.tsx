import { createContext, useContext, useState } from "react";

type TabMemoryContextType = {
  getTabValue: (options: string[]) => string | undefined;
  setTabValue: (options: string[], value: string) => void;
};

const TabMemoryContext = createContext<TabMemoryContextType | undefined>(undefined);

const STORAGE_KEY = "mirascope-tabbed-section-memory";

// Helper to load from localStorage safely
function loadFromStorage(): Record<string, string> {
  if (typeof window === "undefined") return {};

  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch (e) {
    console.error("Failed to load tabbed section memory from localStorage", e);
    return {};
  }
}

export function TabbedSectionMemoryProvider({ children }: { children: React.ReactNode }) {
  const [tabMemory, setTabMemory] = useState<Record<string, string>>(loadFromStorage);

  const getTabValue = (options: string[]): string | undefined => {
    const key = createTabKey(options);
    return tabMemory[key];
  };

  const setTabValue = (options: string[], value: string) => {
    const key = createTabKey(options);
    const newMemory = { ...tabMemory, [key]: value };

    // Save to localStorage
    if (typeof window !== "undefined") {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newMemory));
      } catch (e) {
        console.error("Failed to save tabbed section memory to localStorage", e);
      }
    }

    setTabMemory(newMemory);
  };

  return (
    <TabMemoryContext.Provider value={{ getTabValue, setTabValue }}>
      {children}
    </TabMemoryContext.Provider>
  );
}

// Helper to create a consistent key from tab options
function createTabKey(options: string[]): string {
  return options.sort().join("__");
}

// Custom hook to use the tab memory
export function useTabMemory() {
  const context = useContext(TabMemoryContext);
  if (context === undefined) {
    throw new Error("useTabMemory must be used within a TabbedSectionMemoryProvider");
  }
  return context;
}
