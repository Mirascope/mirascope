import { Context } from "effect";

export type Settings = {
  readonly env: string;
  readonly DATABASE_URL?: string;
  readonly GOOGLE_CLIENT_ID?: string;
  readonly GOOGLE_CLIENT_SECRET?: string;
  readonly GOOGLE_CALLBACK_URL?: string;
  readonly GITHUB_CLIENT_ID?: string;
  readonly GITHUB_CLIENT_SECRET?: string;
  readonly GITHUB_CALLBACK_URL?: string;
  readonly SITE_URL?: string;
  // ROUTER KEYS
  readonly ANTHROPIC_API_KEY?: string;
  readonly GEMINI_API_KEY?: string;
  readonly OPENAI_API_KEY?: string;
};

export class SettingsService extends Context.Tag("SettingsService")<
  SettingsService,
  Settings
>() {}

export function getSettings(): Settings {
  return {
    env: process.env.ENVIRONMENT || "local",
    DATABASE_URL: process.env.DATABASE_URL,
    GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET: process.env.GITHUB_CLIENT_SECRET,
    GITHUB_CALLBACK_URL: process.env.GITHUB_CALLBACK_URL,
    GOOGLE_CLIENT_ID: process.env.GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET,
    GOOGLE_CALLBACK_URL: process.env.GOOGLE_CALLBACK_URL,
    SITE_URL: process.env.SITE_URL,
    // ROUTER KEYS
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    GEMINI_API_KEY: process.env.GEMINI_API_KEY,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  };
}
