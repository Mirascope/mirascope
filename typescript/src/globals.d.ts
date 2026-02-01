/**
 * Global type overrides for TypeScript SDK.
 *
 * Bun extends the standard Headers interface with additional methods (toJSON, count, getAll).
 * This causes type errors with the Fern-generated API client which uses a standard Headers polyfill.
 *
 * This file makes Bun's extra Headers methods optional, allowing the standard polyfill to be
 * type-compatible while preserving the ability to use these methods when available.
 */

declare global {
  interface Headers {
    // Make Bun-specific methods optional so standard Headers implementations are compatible
    toJSON?(): Record<string, string>;
    count?: number;
    getAll?(name: string): string[];
  }
}

export {};
