import { describe, it, expect } from "vitest";
import { getWebHandler } from "@/api/handler";
import { handleRequest } from "@/api/handler";

describe("getWebHandler", () => {
  it("should cache the handler for the same environment", () => {
    const handler1 = getWebHandler();
    const handler2 = getWebHandler();
    expect(handler1).toBe(handler2);
  });

  it("should create a new handler for a different environment", () => {
    const handler1 = getWebHandler({ environment: "test" });
    const handler2 = getWebHandler({ environment: "production" });
    expect(handler1).not.toBe(handler2);
  });
});

describe("handleRequest", () => {
  it("should return matched=false and 404 for a non-existing route", async () => {
    const req = new Request("http://localhost/api/v0", { method: "GET" });
    const { matched, response } = await handleRequest(req, {
      environment: "test",
      prefix: "/api/v0",
    });

    expect(matched).toBe(false);
    expect(response.status).toBe(404);
  });

  it("should return 500 and matched=false for a request that triggers an exception", async () => {
    const faultyRequest = new Proxy(
      {},
      {
        get() {
          throw new Error("boom");
        },
      },
    ) as Request;

    const { matched, response } = await handleRequest(faultyRequest, {
      environment: "test",
    });

    expect(matched).toBe(false);
    expect(response.status).toBe(500);
    const text = await response.text();
    expect(text).toMatch(/Internal Server Error/);
  });
});
