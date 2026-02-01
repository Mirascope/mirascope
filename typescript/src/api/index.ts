/**
 * Mirascope Cloud API client module.
 */

export {
  MirascopeClient,
  getClient,
  resetClient,
  type MirascopeClientOptions,
} from "./client.js";
export {
  getSettings,
  updateSettings,
  resetSettings,
  type MirascopeSettings,
} from "./settings.js";

// Re-export types from generated client that users may need
export { MirascopeEnvironment } from "./_generated/environments.js";
