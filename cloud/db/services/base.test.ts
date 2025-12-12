import { describe, it, expect } from "vitest";
import { Effect, Cause, Exit } from "effect";
import type { PostgresJsDatabase } from "drizzle-orm/postgres-js";

import type * as schema from "@/db/schema";
import { BaseService } from "@/db/services/base";
import { sessions } from "@/db/schema/sessions";

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
  });
});
