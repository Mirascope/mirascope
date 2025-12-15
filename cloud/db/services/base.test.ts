import { describe, it, expect } from "vitest";
import { Effect, Cause, Exit } from "effect";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";
import { and, eq } from "drizzle-orm";

import type * as schema from "@/db/schema";
import { BaseService } from "@/db/services/base";
import { sessions } from "@/db/schema/sessions";
import { organizationMemberships } from "@/db/schema/organization-memberships";

class MisconfiguredSessionService extends BaseService<
  { id: string; expiresAt: Date },
  "foos/:fooId/sessions/:sessionId",
  typeof sessions
> {
  protected getTable() {
    return sessions;
  }

  protected getResourceName() {
    return "session";
  }

  protected getIdParamName() {
    return "sessionId" as const;
  }

  protected getPublicFields() {
    return {
      id: sessions.id,
      expiresAt: sessions.expiresAt,
    };
  }
}

/**
 * Test service with multiple parent path params.
 * Path: organizations/:organizationId/users/:userId/memberships/:id
 * Parent params: { organizationId, userId } - both exist as columns on the table
 */
class MultiParentService extends BaseService<
  { id: string },
  "organizations/:organizationId/users/:userId/memberships/:id",
  typeof organizationMemberships
> {
  protected getTable() {
    return organizationMemberships;
  }

  protected getResourceName() {
    return "membership";
  }

  protected getIdParamName() {
    return "id" as const;
  }

  protected getPublicFields() {
    return {
      id: organizationMemberships.id,
    };
  }

  // Expose protected method for testing
  public testGetParentScopedWhere(params: {
    organizationId: string;
    userId: string;
  }) {
    return this.getParentScopedWhere(params);
  }
}

describe("BaseService", () => {
  describe("nested scoping", () => {
    it("throws a clear error when a parent path param doesn't map to a table column", async () => {
      // We never reach the DB call; this is only to satisfy the constructor.
      const db = {} as PostgresJsDatabase<typeof schema>;
      const service = new MisconfiguredSessionService(db);

      const exit = await Effect.runPromiseExit(
        service.findById({
          fooId: "foo-id",
          sessionId: "00000000-0000-0000-0000-000000000000",
        }),
      );

      expect(Exit.isFailure(exit)).toBe(true);
      if (Exit.isFailure(exit)) {
        // This is a defect (thrown Error), not a typed failure.
        expect(Cause.isDie(exit.cause)).toBe(true);
        const pretty = Cause.pretty(exit.cause);
        expect(pretty).toContain(
          "BaseService misconfiguration: table 'session' is missing column 'fooId' for path param scoping. Ensure the column name matches the path parameter name.",
        );
      }
    });

    it("combines multiple parent params with AND when there are more than one", () => {
      const db = {} as PostgresJsDatabase<typeof schema>;
      const service = new MultiParentService(db);

      const whereClause = service.testGetParentScopedWhere({
        organizationId: "org-123",
        userId: "user-456",
      });

      // Verify we get an AND condition combining both parent params
      const expectedWhere = and(
        eq(organizationMemberships.organizationId, "org-123"),
        eq(organizationMemberships.userId, "user-456"),
      );

      // Compare the SQL structure
      expect(whereClause).toEqual(expectedWhere);
    });
  });
});
