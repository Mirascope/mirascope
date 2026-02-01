/**
 * Type representing no variables for prompts and calls.
 * `Record<never, never>` creates an object type with no keys,
 * ensuring `keyof NoVars` is `never`.
 */
export type NoVars = Record<never, never>;
