/* v8 ignore file -- pure error class definitions, no branching logic */
import { Data } from "effect";

export class OAuthError extends Data.TaggedError("OAuthError")<{
  readonly message: string;
  readonly provider?: string;
  readonly cause?: unknown;
}> {}

export class InvalidStateError extends Data.TaggedError("InvalidStateError")<{
  readonly message: string;
}> {}

export class MissingCredentialsError extends Data.TaggedError(
  "MissingCredentialsError",
)<{
  readonly message: string;
  readonly provider: string;
}> {}

export class AuthenticationFailedError extends Data.TaggedError(
  "AuthenticationFailedError",
)<{
  readonly message: string;
  readonly cause?: unknown;
}> {}
