import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  createStaticRouteHead,
  getStaticRouteTitle,
  getStaticRoutes,
} from "./static-route-head";

describe("createStaticRouteHead", () => {
  it("creates head function for registered route", () => {
    const head = createStaticRouteHead("/");
    const result = head();

    expect(result.meta).toBeDefined();
    expect(result.links).toBeDefined();

    // Check title is set correctly
    const titleMeta = result.meta.find((m) => "title" in m) as
      | { title: string }
      | undefined;
    expect(titleMeta?.title).toBe("Home | Mirascope");

    // Check description is set
    const descMeta = result.meta.find(
      (m) => "name" in m && m.name === "description",
    ) as { name: string; content: string } | undefined;
    expect(descMeta?.content).toBe("The complete toolkit for AI engineers");
  });

  it("creates head function for pricing route", () => {
    const head = createStaticRouteHead("/pricing");
    const result = head();

    const titleMeta = result.meta.find((m) => "title" in m) as
      | { title: string }
      | undefined;
    expect(titleMeta?.title).toBe("Pricing | Mirascope");
  });

  it("creates head function for blog index route", () => {
    const head = createStaticRouteHead("/blog/");
    const result = head();

    const titleMeta = result.meta.find((m) => "title" in m) as
      | { title: string }
      | undefined;
    expect(titleMeta?.title).toBe("Blog | Mirascope");
  });

  it("creates head function for docs route", () => {
    const head = createStaticRouteHead("/docs");
    const result = head();

    const titleMeta = result.meta.find((m) => "title" in m) as
      | { title: string }
      | undefined;
    expect(titleMeta?.title).toBe("Documentation | Mirascope");
  });

  it("throws error for unregistered route", () => {
    // Using type assertion to test error handling for invalid routes
    expect(() =>
      createStaticRouteHead(
        "/unregistered" as Parameters<typeof createStaticRouteHead>[0],
      ),
    ).toThrow('[static-routes] Route "/unregistered" is not registered');
  });

  it("generates canonical URL correctly", () => {
    const head = createStaticRouteHead("/pricing");
    const result = head();

    const canonicalLink = result.links?.find((l) => l.rel === "canonical");
    expect(canonicalLink?.href).toBe("https://mirascope.com/pricing");
  });

  it("generates Open Graph tags", () => {
    const head = createStaticRouteHead("/");
    const result = head();

    const ogType = result.meta.find(
      (m) => "property" in m && m.property === "og:type",
    ) as { property: string; content: string } | undefined;
    expect(ogType?.content).toBe("website");

    const ogTitle = result.meta.find(
      (m) => "property" in m && m.property === "og:title",
    ) as { property: string; content: string } | undefined;
    expect(ogTitle?.content).toBe("Home | Mirascope");
  });

  it("generates Twitter tags", () => {
    const head = createStaticRouteHead("/");
    const result = head();

    const twitterCard = result.meta.find(
      (m) => "name" in m && m.name === "twitter:card",
    ) as { name: string; content: string } | undefined;
    expect(twitterCard?.content).toBe("summary_large_image");
  });
});

describe("getStaticRouteTitle", () => {
  beforeEach(() => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("returns title for registered route", () => {
    const title = getStaticRouteTitle("/");
    expect(title).toBe("Home");
    expect(console.warn).not.toHaveBeenCalled();
  });

  it("returns title for pricing route", () => {
    const title = getStaticRouteTitle("/pricing");
    expect(title).toBe("Pricing");
    expect(console.warn).not.toHaveBeenCalled();
  });

  it("returns title for blog index route", () => {
    const title = getStaticRouteTitle("/blog/");
    expect(title).toBe("Blog");
    expect(console.warn).not.toHaveBeenCalled();
  });

  it("returns title for docs route", () => {
    const title = getStaticRouteTitle("/docs");
    expect(title).toBe("Documentation");
    expect(console.warn).not.toHaveBeenCalled();
  });

  it("returns null and logs warning for unregistered route", () => {
    const title = getStaticRouteTitle("/unknown-route");
    expect(title).toBeNull();
    expect(console.warn).toHaveBeenCalledWith(
      "[static-routes] No metadata found for route: /unknown-route",
    );
  });

  it("returns null and logs warning for empty string", () => {
    const title = getStaticRouteTitle("");
    expect(title).toBeNull();
    expect(console.warn).toHaveBeenCalledWith(
      "[static-routes] No metadata found for route: ",
    );
  });
});

describe("getStaticRoutes", () => {
  it("returns all registered static routes", () => {
    const routes = getStaticRoutes();

    expect(routes).toContain("/");
    expect(routes).toContain("/pricing");
    expect(routes).toContain("/blog/");
    expect(routes).toContain("/docs");
    expect(routes.length).toBe(4);
  });

  it("returns routes as strings", () => {
    const routes = getStaticRoutes();

    for (const route of routes) {
      expect(typeof route).toBe("string");
    }
  });
});
