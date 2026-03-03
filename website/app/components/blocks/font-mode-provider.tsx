import React, { createContext, useContext, useEffect, useState } from "react";

type FontMode = "default" | "fun" | "professional";

type FontModeProviderProps = {
  children: React.ReactNode;
  defaultFontMode?: FontMode;
  storageKey?: string;
};

type FontModeProviderState = {
  fontMode: FontMode;
  setFontMode: (fontMode: FontMode) => void;
};

const initialState: FontModeProviderState = {
  fontMode: "default",
  setFontMode: () => null,
};

const FontModeProviderContext =
  createContext<FontModeProviderState>(initialState);

export function FontModeProvider({
  children,
  defaultFontMode = "default",
  storageKey = "mirascope-ui-font-mode",
  ...props
}: FontModeProviderProps) {
  const [fontMode, setFontMode] = useState<FontMode>(
    () => (localStorage.getItem(storageKey) as FontMode) || defaultFontMode,
  );

  useEffect(() => {
    const root = window.document.documentElement;

    root.classList.remove("fun-mode", "professional-mode");

    if (fontMode === "default") {
      // Default mode doesn't need a class
    } else {
      root.classList.add(`${fontMode}-mode`);
    }
  }, [fontMode]);

  const value = {
    fontMode,
    setFontMode: (fontMode: FontMode) => {
      localStorage.setItem(storageKey, fontMode);
      setFontMode(fontMode);
    },
  };

  return (
    <FontModeProviderContext.Provider {...props} value={value}>
      {children}
    </FontModeProviderContext.Provider>
  );
}

export const useFontMode = () => {
  const context = useContext(FontModeProviderContext);

  if (context === undefined)
    throw new Error("useFontMode must be used within a FontModeProvider");

  return context;
};
