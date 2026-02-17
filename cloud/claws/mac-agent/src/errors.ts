/**
 * Typed errors for the Mac Mini Agent.
 */
import { Data } from "effect";

export class ProvisioningError extends Data.TaggedError("ProvisioningError")<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export class DeprovisioningError extends Data.TaggedError(
  "DeprovisioningError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export class AuthError extends Data.TaggedError("AuthError")<{
  readonly message: string;
}> {}

export class ExecError extends Data.TaggedError("ExecError")<{
  readonly message: string;
  readonly command: string;
  readonly exitCode: number;
  readonly stderr: string;
}> {}

export class NotFoundError extends Data.TaggedError("NotFoundError")<{
  readonly message: string;
}> {}

export class CapacityError extends Data.TaggedError("CapacityError")<{
  readonly message: string;
  readonly current: number;
  readonly max: number;
}> {}

export class ValidationError extends Data.TaggedError("ValidationError")<{
  readonly message: string;
}> {}

export class SystemError extends Data.TaggedError("SystemError")<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export function errorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return String(error);
}
