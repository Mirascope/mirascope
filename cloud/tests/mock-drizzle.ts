/**
 * Mock DrizzleORM layer for tests that don't need real database operations.
 *
 * This file is separate from tests/db.ts to avoid circular dependencies with tests/payments.ts
 */

import { Layer, Effect } from "effect";
import { DrizzleORM, type DrizzleORMClient } from "@/db/client";

/**
 * Simple mock DrizzleORM layer for tests that don't need real database operations.
 *
 * This provides a minimal DrizzleORM implementation that:
 * - Returns empty arrays for select queries (with sum: "0" for aggregations)
 * - Returns mock IDs for insert operations
 * - Returns mock IDs for update operations
 * - Returns empty arrays for delete operations
 * - No-ops transactions (just runs the effect directly)
 *
 * Use this when testing code that requires DrizzleORM but doesn't need actual
 * database state (e.g., payment operations where you want to test business logic
 * without hitting a real database).
 *
 * For tests that need actual database state and transactions, use TestDrizzleORM
 * or TestDatabase instead.
 */
export const MockDrizzleORMLayer = Layer.succeed(DrizzleORM, {
  select: () => ({
    from: () => ({
      where: () => ({
        pipe: () => Effect.succeed([{ sum: "0" }]),
      }),
    }),
  }),
  insert: () => ({
    values: () => ({
      returning: () => ({
        pipe: () => Effect.succeed([{ id: `mock_${crypto.randomUUID()}` }]),
      }),
    }),
  }),
  update: () => ({
    set: () => ({
      where: () => ({
        returning: () => ({
          pipe: () => Effect.succeed([{ id: `mock_${crypto.randomUUID()}` }]),
        }),
      }),
    }),
  }),
  delete: () => ({
    where: () => ({
      returning: () => ({
        pipe: () => Effect.succeed([]),
      }),
    }),
  }),
  withTransaction: <A, E, R>(effect: Effect.Effect<A, E, R>) => effect,
} as unknown as DrizzleORMClient);
