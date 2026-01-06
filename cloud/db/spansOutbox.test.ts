import { describe, it, expect } from "vitest";
import { spansOutbox, outboxStatusEnum } from "@/db/schema/spansOutbox";
import { getTableName } from "drizzle-orm";

describe("spansOutbox schema", () => {
  describe("table definition", () => {
    it("has correct table name", () => {
      expect(getTableName(spansOutbox)).toBe("spans_outbox");
    });

    it("has all required columns", () => {
      const columns = Object.keys(spansOutbox);
      expect(columns).toContain("id");
      expect(columns).toContain("spanId");
      expect(columns).toContain("operation");
      expect(columns).toContain("status");
      expect(columns).toContain("retryCount");
      expect(columns).toContain("lastError");
      expect(columns).toContain("lockedAt");
      expect(columns).toContain("lockedBy");
      expect(columns).toContain("createdAt");
      expect(columns).toContain("processAfter");
      expect(columns).toContain("processedAt");
    });
  });

  describe("outboxStatusEnum", () => {
    it("has all expected values", () => {
      expect(outboxStatusEnum.enumValues).toEqual([
        "pending",
        "processing",
        "completed",
        "failed",
      ]);
    });
  });
});
