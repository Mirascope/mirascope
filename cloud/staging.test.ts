import { describe, it, expect, vi } from "vitest";

import type { WorkerEnv } from "./workers/config";

import { wrapWithStagingMiddleware } from "./staging";

const STAGING_HOSTNAME = "staging.mirascope.com";

const createMockEnv = (
  assetsFetch?: (req: Request) => Promise<Response>,
): Partial<WorkerEnv> => ({
  ASSETS: {
    fetch:
      assetsFetch ??
      vi.fn().mockResolvedValue(new Response(null, { status: 404 })),
  } as WorkerEnv["ASSETS"],
});

const mockExecutionContext = {
  waitUntil: vi.fn(),
  passThroughOnException: vi.fn(),
  props: undefined,
} as unknown as ExecutionContext;

describe("wrapWithStagingMiddleware", () => {
  describe("staging authentication", () => {
    it("returns 401 when no auth and no session cookie on staging", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`);
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(401);
      expect(response.headers.get("WWW-Authenticate")).toBe(
        'Basic realm="Staging"',
      );
      expect(coreHandler).not.toHaveBeenCalled();
      expect(ssrHandler).not.toHaveBeenCalled();
    });

    it("returns 401 for invalid credentials on staging", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`, {
        headers: { Authorization: `Basic ${btoa("wrong:credentials")}` },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(401);
      expect(coreHandler).not.toHaveBeenCalled();
    });

    it("returns 302 with session cookie for valid credentials on staging", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`, {
        headers: { Authorization: `Basic ${btoa("mirascope:mirascope")}` },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(302);
      expect(response.headers.get("Location")).toBe(
        `https://${STAGING_HOSTNAME}/dashboard`,
      );
      expect(response.headers.get("Set-Cookie")).toContain(
        "staging_session=ok",
      );
      expect(response.headers.get("Set-Cookie")).toContain("HttpOnly");
      expect(response.headers.get("Set-Cookie")).toContain("SameSite=Strict");
      expect(response.headers.get("Set-Cookie")).toContain("Max-Age=86400");
      expect(coreHandler).not.toHaveBeenCalled();
    });

    it("continues to core handler with valid session cookie on staging", async () => {
      const coreHandler = vi.fn(async () => new Response("Core handled"));
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`, {
        headers: { Cookie: "staging_session=ok" },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(200);
      expect(await response.text()).toBe("Core handled");
      expect(coreHandler).toHaveBeenCalled();
    });

    it("bypasses auth for /auth/* routes on staging", async () => {
      const coreHandler = vi.fn(async () => new Response("Auth route"));
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/auth/callback`);
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(200);
      expect(await response.text()).toBe("Auth route");
      expect(coreHandler).toHaveBeenCalled();
    });

    it("handles session cookie among other cookies", async () => {
      const coreHandler = vi.fn(async () => new Response("OK"));
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`, {
        headers: { Cookie: "other=value; staging_session=ok; another=thing" },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(200);
      expect(coreHandler).toHaveBeenCalled();
    });
  });

  describe("staging assets", () => {
    it("serves assets from ASSETS binding on staging", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("SSR"));
      const mockFetch = vi
        .fn()
        .mockResolvedValue(new Response("Asset content", { status: 200 }));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv(mockFetch) as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/style.css`, {
        headers: { Cookie: "staging_session=ok" },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(await response.text()).toBe("Asset content");
      expect(coreHandler).toHaveBeenCalled();
      expect(ssrHandler).not.toHaveBeenCalled();
    });

    it("falls through to SSR when asset not found on staging", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("SSR Response"));
      const mockFetch = vi
        .fn()
        .mockResolvedValue(new Response(null, { status: 404 }));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv(mockFetch) as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/page`, {
        headers: { Cookie: "staging_session=ok" },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(await response.text()).toBe("SSR Response");
      expect(ssrHandler).toHaveBeenCalled();
    });
  });

  describe("production requests", () => {
    it("skips staging handlers for production hostname", async () => {
      const coreHandler = vi.fn(async () => null);
      const ssrHandler = vi.fn(async () => new Response("Production SSR"));
      const mockFetch = vi.fn();

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv(mockFetch) as WorkerEnv;

      const request = new Request("https://mirascope.com/page");
      const response = await fetch(request, env, mockExecutionContext);

      expect(await response.text()).toBe("Production SSR");
      expect(coreHandler).toHaveBeenCalled();
      expect(ssrHandler).toHaveBeenCalled();
      // ASSETS.fetch should not be called for production
      expect(mockFetch).not.toHaveBeenCalled();
    });

    it("does not require auth for production requests", async () => {
      const coreHandler = vi.fn(async () => new Response("Core"));
      const ssrHandler = vi.fn(async () => new Response("SSR"));

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      // No auth header, no cookie - should work fine on production
      const request = new Request("https://mirascope.com/dashboard");
      const response = await fetch(request, env, mockExecutionContext);

      expect(response.status).toBe(200);
      expect(await response.text()).toBe("Core");
    });
  });

  describe("execution order", () => {
    it("runs staging auth before core handler", async () => {
      const callOrder: string[] = [];

      const coreHandler = vi.fn(async () => {
        callOrder.push("core");
        return null;
      });
      const ssrHandler = vi.fn(async () => {
        callOrder.push("ssr");
        return new Response("SSR");
      });

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv() as WorkerEnv;

      // No auth - should stop at auth
      const request = new Request(`https://${STAGING_HOSTNAME}/dashboard`);
      await fetch(request, env, mockExecutionContext);

      expect(callOrder).toEqual([]);
    });

    it("runs core handler before staging assets and SSR", async () => {
      const callOrder: string[] = [];

      const coreHandler = vi.fn(async () => {
        callOrder.push("core");
        return null;
      });
      const ssrHandler = vi.fn(async () => {
        callOrder.push("ssr");
        return new Response("SSR");
      });
      const mockFetch = vi.fn(async () => {
        callOrder.push("assets");
        return new Response(null, { status: 404 });
      });

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv(mockFetch) as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/page`, {
        headers: { Cookie: "staging_session=ok" },
      });
      await fetch(request, env, mockExecutionContext);

      expect(callOrder).toEqual(["core", "assets", "ssr"]);
    });

    it("short-circuits when core handler returns response", async () => {
      const coreHandler = vi.fn(async () => new Response("Core response"));
      const ssrHandler = vi.fn(async () => new Response("SSR"));
      const mockFetch = vi.fn();

      const fetch = wrapWithStagingMiddleware(coreHandler, ssrHandler);
      const env = createMockEnv(mockFetch) as WorkerEnv;

      const request = new Request(`https://${STAGING_HOSTNAME}/page`, {
        headers: { Cookie: "staging_session=ok" },
      });
      const response = await fetch(request, env, mockExecutionContext);

      expect(await response.text()).toBe("Core response");
      expect(mockFetch).not.toHaveBeenCalled();
      expect(ssrHandler).not.toHaveBeenCalled();
    });
  });
});
