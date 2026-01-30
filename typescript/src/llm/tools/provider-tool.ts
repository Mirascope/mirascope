/**
 * Base class for provider-native tools.
 *
 * Unlike regular tools which define functions that you execute locally,
 * provider tools are capabilities built into the provider's API.
 * The provider handles execution entirely server-side.
 */
export class ProviderTool {
  readonly name: string;

  constructor(name: string) {
    this.name = name;
  }
}

/**
 * Type guard to check if a value is a ProviderTool.
 */
export function isProviderTool(value: unknown): value is ProviderTool {
  return value instanceof ProviderTool;
}
