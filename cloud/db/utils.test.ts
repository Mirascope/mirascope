import { describe, it, expect } from "vitest";
import { isCheckConstraintError, isUniqueConstraintError } from "@/db/utils";

describe("isUniqueConstraintError", () => {
  it("returns false for null", () => {
    expect(isUniqueConstraintError(null)).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isUniqueConstraintError(undefined)).toBe(false);
  });

  it("returns false for non-object values", () => {
    expect(isUniqueConstraintError("string")).toBe(false);
    expect(isUniqueConstraintError(123)).toBe(false);
    expect(isUniqueConstraintError(true)).toBe(false);
  });

  it("returns false for objects without code property", () => {
    expect(isUniqueConstraintError({})).toBe(false);
    expect(isUniqueConstraintError({ message: "error" })).toBe(false);
  });

  it("returns false for objects with non-matching code", () => {
    expect(isUniqueConstraintError({ code: "12345" })).toBe(false);
    expect(isUniqueConstraintError({ code: "00000" })).toBe(false);
  });

  it("returns true for direct PostgreSQL unique violation error", () => {
    expect(isUniqueConstraintError({ code: "23505" })).toBe(true);
  });

  it("returns false for wrapped error with non-object cause", () => {
    expect(isUniqueConstraintError({ cause: null })).toBe(false);
    expect(isUniqueConstraintError({ cause: "string" })).toBe(false);
    expect(isUniqueConstraintError({ cause: 123 })).toBe(false);
  });

  it("returns false for wrapped error with cause missing code", () => {
    expect(isUniqueConstraintError({ cause: {} })).toBe(false);
    expect(isUniqueConstraintError({ cause: { message: "error" } })).toBe(
      false,
    );
  });

  it("returns false for wrapped error with non-matching cause code", () => {
    expect(isUniqueConstraintError({ cause: { code: "12345" } })).toBe(false);
  });

  it("returns true for Drizzle-wrapped PostgreSQL unique violation error", () => {
    // This simulates how Drizzle wraps PostgreSQL errors
    expect(isUniqueConstraintError({ cause: { code: "23505" } })).toBe(true);
  });

  it("returns true for full Drizzle error structure", () => {
    // Simulate a real Drizzle error with all properties
    const drizzleError = {
      message:
        'Failed query: insert into "users" ...\nparams: test@example.com',
      query: 'insert into "users" ...',
      params: ["test@example.com"],
      cause: {
        message:
          'duplicate key value violates unique constraint "users_email_unique"',
        code: "23505",
        detail: "Key (email)=(test@example.com) already exists.",
        severity: "ERROR",
      },
    };
    expect(isUniqueConstraintError(drizzleError)).toBe(true);
  });
});

describe("isCheckConstraintError", () => {
  it("returns false for null", () => {
    expect(isCheckConstraintError(null)).toBe(false);
  });

  it("returns false for undefined", () => {
    expect(isCheckConstraintError(undefined)).toBe(false);
  });

  it("returns false for non-object values", () => {
    expect(isCheckConstraintError("string")).toBe(false);
    expect(isCheckConstraintError(123)).toBe(false);
    expect(isCheckConstraintError(true)).toBe(false);
  });

  it("returns false for objects without code property", () => {
    expect(isCheckConstraintError({})).toBe(false);
    expect(isCheckConstraintError({ message: "error" })).toBe(false);
  });

  it("returns false for objects with non-matching code", () => {
    expect(isCheckConstraintError({ code: "12345" })).toBe(false);
    expect(isCheckConstraintError({ code: "23505" })).toBe(false); // unique violation
  });

  it("returns true for direct PostgreSQL check violation error", () => {
    expect(isCheckConstraintError({ code: "23514" })).toBe(true);
  });

  it("returns false for wrapped error with non-object cause", () => {
    expect(isCheckConstraintError({ cause: null })).toBe(false);
    expect(isCheckConstraintError({ cause: "string" })).toBe(false);
    expect(isCheckConstraintError({ cause: 123 })).toBe(false);
  });

  it("returns false for wrapped error with cause missing code", () => {
    expect(isCheckConstraintError({ cause: {} })).toBe(false);
    expect(isCheckConstraintError({ cause: { message: "error" } })).toBe(false);
  });

  it("returns false for wrapped error with non-matching cause code", () => {
    expect(isCheckConstraintError({ cause: { code: "12345" } })).toBe(false);
  });

  it("returns true for Drizzle-wrapped PostgreSQL check violation error", () => {
    // This simulates how Drizzle wraps PostgreSQL errors
    expect(isCheckConstraintError({ cause: { code: "23514" } })).toBe(true);
  });

  it("returns true for full Drizzle error structure", () => {
    // Simulate a real Drizzle error with all properties
    const drizzleError = {
      message: 'Failed query: insert into "projects" ...',
      query: 'insert into "projects" ...',
      params: ["Test Project", "user-id", "org-id"],
      cause: {
        message:
          'new row for relation "projects" violates check constraint "check_one_owner"',
        code: "23514",
        constraint: "check_one_owner",
        severity: "ERROR",
      },
    };
    expect(isCheckConstraintError(drizzleError)).toBe(true);
  });
});
