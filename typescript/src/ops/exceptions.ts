/**
 * Exception classes for the Mirascope ops module.
 */

import { MirascopeError } from "@/llm/exceptions";

/**
 * Raised when ops configuration is invalid.
 */
export class ConfigurationError extends MirascopeError {
  constructor(message: string) {
    super(message);
  }
}

/**
 * Raised when function closure cannot be computed.
 */
export class ClosureComputationError extends MirascopeError {
  readonly qualifiedName: string;

  constructor(qualifiedName: string, message: string) {
    super(message);
    this.qualifiedName = qualifiedName;
  }
}
