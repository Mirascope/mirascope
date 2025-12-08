import { Data } from "effect";

export class NotFoundError extends Data.TaggedError("NotFoundError")<{
  readonly message: string;
  readonly resource?: string;
}> {}

export class DatabaseError extends Data.TaggedError("DatabaseError")<{
  readonly message: string;
  readonly cause?: unknown;
}> {}

export class InvalidSessionError extends Data.TaggedError(
  "InvalidSessionError",
)<{
  readonly message: string;
  readonly sessionId?: string;
}> {}
