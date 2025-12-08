import { Context } from "effect";

// ============================================================================
// Context
// ============================================================================

export class EnvironmentService extends Context.Tag("EnvironmentService")<
  EnvironmentService,
  { readonly environment: string }
>() {}
