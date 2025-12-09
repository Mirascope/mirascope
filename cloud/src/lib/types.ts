/**
 * Shared types for Effect runner functions.
 *
 * These types are intentionally in a separate file with no imports to avoid
 * pulling server-side dependencies into client code that only needs the types.
 */

type SuccessResult<A> = { success: true; data: A };
type ErrorResult = { success: false; error: string };
export type Result<A> = SuccessResult<A> | ErrorResult;
