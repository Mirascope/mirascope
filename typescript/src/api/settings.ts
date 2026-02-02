/**
 * Settings management for Mirascope API client.
 */

export interface MirascopeSettings {
  apiKey?: string;
  baseURL: string;
}

const DEFAULT_BASE_URL = "https://mirascope.com/api/v2";

let currentSettings: MirascopeSettings = {
  apiKey: process.env.MIRASCOPE_API_KEY,
  baseURL: process.env.MIRASCOPE_BASE_URL || DEFAULT_BASE_URL,
};

export function getSettings(): MirascopeSettings {
  return { ...currentSettings };
}

export function updateSettings(updates: Partial<MirascopeSettings>): void {
  currentSettings = { ...currentSettings, ...updates };
}

export function resetSettings(): void {
  currentSettings = {
    apiKey: process.env.MIRASCOPE_API_KEY,
    baseURL: process.env.MIRASCOPE_BASE_URL || DEFAULT_BASE_URL,
  };
}
