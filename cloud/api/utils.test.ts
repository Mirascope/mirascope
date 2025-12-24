import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { handleErrors, handleDefects } from "@/api/utils";
import { NotFoundError, UnauthorizedError, DatabaseError } from "@/errors";

describe("handleErrors", () => {
  it("passes through successful Response", async () => {
    const response = new Response("OK", { status: 200 });
    const effect = Effect.succeed(response);

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result).toBe(response);
  });

  it("converts tagged error with status to Response", async () => {
    const effect = Effect.fail(
      new NotFoundError({ message: "Resource not found" }),
    );

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(404);
    expect(await result.json()).toEqual({
      tag: "NotFoundError",
      message: "Resource not found",
    });
  });

  it("converts error with 401 status", async () => {
    const effect = Effect.fail(
      new UnauthorizedError({ message: "Not authorized" }),
    );

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(401);
    expect(await result.json()).toEqual({
      tag: "UnauthorizedError",
      message: "Not authorized",
    });
  });

  it("converts error with 500 status", async () => {
    const effect = Effect.fail(
      new DatabaseError({ message: "Database error" }),
    );

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "DatabaseError",
      message: "Database error",
    });
  });

  it("handles plain Error (no status, uses message)", async () => {
    const effect = Effect.fail(new Error("Something went wrong"));

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "Something went wrong",
    });
  });

  it("handles object with message property", async () => {
    const effect = Effect.fail({ message: "Custom error message" });

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "Custom error message",
    });
  });

  it("handles object with _tag but no status", async () => {
    const effect = Effect.fail({
      _tag: "CustomError",
      message: "Custom tagged error",
    });

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "CustomError",
      message: "Custom tagged error",
    });
  });

  it("handles primitive string error", async () => {
    const effect = Effect.fail("string error");

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An error occurred",
    });
  });

  it("handles null error", async () => {
    const effect = Effect.fail(null);

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An error occurred",
    });
  });

  it("handles undefined error", async () => {
    const effect = Effect.fail(undefined);

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An error occurred",
    });
  });

  it("sets Content-Type header to application/json", async () => {
    const effect = Effect.fail(new Error("test"));

    const result = await Effect.runPromise(handleErrors(effect));

    expect(result.headers.get("Content-Type")).toBe("application/json");
  });
});

describe("handleDefects", () => {
  it("passes through successful Response", async () => {
    const response = new Response("OK", { status: 200 });
    const effect = Effect.succeed(response);

    const result = await Effect.runPromise(handleDefects(effect));

    expect(result).toBe(response);
  });

  it("converts Error defect to InternalError response", async () => {
    const effect = Effect.die(new Error("Unexpected failure"));

    const result = await Effect.runPromise(handleDefects(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "Unexpected failure",
    });
  });

  it("converts non-Error defect to generic InternalError response", async () => {
    const effect = Effect.die("string defect");

    const result = await Effect.runPromise(handleDefects(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An unexpected error occurred",
    });
  });

  it("converts object defect to generic InternalError response", async () => {
    const effect = Effect.die({ some: "object" });

    const result = await Effect.runPromise(handleDefects(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An unexpected error occurred",
    });
  });

  it("converts null defect to generic InternalError response", async () => {
    const effect = Effect.die(null);

    const result = await Effect.runPromise(handleDefects(effect));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "An unexpected error occurred",
    });
  });
});

describe("handleErrors and handleDefects together", () => {
  it("handleErrors catches errors, handleDefects passes through", async () => {
    const effect = Effect.fail(
      new NotFoundError({ message: "Not found" }),
    ) as Effect.Effect<Response, NotFoundError, never>;

    const result = await Effect.runPromise(
      effect.pipe(handleErrors, handleDefects),
    );

    expect(result.status).toBe(404);
    expect(await result.json()).toEqual({
      tag: "NotFoundError",
      message: "Not found",
    });
  });

  it("handleDefects catches defects after handleErrors", async () => {
    const effect = Effect.die(new Error("boom")) as Effect.Effect<
      Response,
      never,
      never
    >;

    const result = await Effect.runPromise(effect.pipe(handleDefects));

    expect(result.status).toBe(500);
    expect(await result.json()).toEqual({
      tag: "InternalError",
      message: "boom",
    });
  });
});
