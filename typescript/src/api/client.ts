/**
 * Enhanced Mirascope API client with settings integration.
 */

import { MirascopeClient as BaseMirascopeClient } from "./_generated/Client.js";
import { getSettings } from "./settings.js";

export interface MirascopeClientOptions {
  apiKey?: string;
  baseURL?: string;
  timeoutInSeconds?: number;
  maxRetries?: number;
}

export class MirascopeClient extends BaseMirascopeClient {
  constructor(options: MirascopeClientOptions = {}) {
    const settings = getSettings();
    const apiKey = options.apiKey ?? settings.apiKey;
    const baseURL = options.baseURL ?? settings.baseURL;

    super({
      baseUrl: baseURL,
      timeoutInSeconds: options.timeoutInSeconds ?? 180,
      maxRetries: options.maxRetries ?? 2,
      headers: apiKey
        ? { Authorization: `Bearer ${apiKey}` }
        : /* v8 ignore next 1 */ undefined,
    });
  }
}

let cachedClient: MirascopeClient | null = null;

export function getClient(options?: MirascopeClientOptions): MirascopeClient {
  if (!options && cachedClient) {
    return cachedClient;
  }
  const client = new MirascopeClient(options);
  if (!options) {
    cachedClient = client;
  }
  return client;
}

export function resetClient(): void {
  cachedClient = null;
}
