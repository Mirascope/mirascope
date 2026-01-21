import { describe, it, expect } from "vitest";
import { handleRedirect } from "./redirects";

const createRequest = (path: string): Request =>
  new Request(`https://mirascope.com${path}`);

describe("handleRedirect", () => {
  describe("simple redirects", () => {
    it("redirects /discord-invite to Discord URL with 301", () => {
      const response = handleRedirect(createRequest("/discord-invite"));

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://discord.gg/gZMNYR4zEs",
      );
    });

    it("redirects /slack-invite to /discord-invite with 302", () => {
      const response = handleRedirect(createRequest("/slack-invite"));

      expect(response).not.toBeNull();
      expect(response!.status).toBe(302);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/discord-invite",
      );
    });

    it("redirects old quickstart path to v1 guides with 301", () => {
      const response = handleRedirect(
        createRequest("/docs/mirascope/getting-started/quickstart"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/v1/guides/getting-started/quickstart",
      );
    });
  });

  describe("underscore path redirects", () => {
    it("redirects tutorials underscore paths to hyphenated docs paths", () => {
      const response = handleRedirect(
        createRequest("/tutorials/agents/blog_writing_agent"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/mirascope/guides/agents/blog-writing-agent",
      );
    });

    it("redirects tutorials paths with trailing content", () => {
      const response = handleRedirect(
        createRequest("/tutorials/agents/sql_agent/extra"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/mirascope/guides/agents/sql-agent",
      );
    });

    it("redirects learn underscore paths to hyphenated docs paths", () => {
      const response = handleRedirect(
        createRequest("/learn/provider_specific/anthropic"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/mirascope/learn/provider-specific/anthropic",
      );
    });

    it("redirects prompt engineering chaining paths", () => {
      const response = handleRedirect(
        createRequest(
          "/tutorials/prompt_engineering/chaining_based/chain_of_verification",
        ),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/mirascope/guides/prompt-engineering/chaining-based/chain-of-verification",
      );
    });

    it("redirects prompt engineering text based paths", () => {
      const response = handleRedirect(
        createRequest(
          "/tutorials/prompt_engineering/text_based/chain_of_thought",
        ),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/mirascope/guides/prompt-engineering/text-based/chain-of-thought",
      );
    });
  });

  describe("prefix redirects", () => {
    it("redirects /integrations/* to legacy site", () => {
      const response = handleRedirect(createRequest("/integrations/logfire"));

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://legacy.mirascope.com/integrations/logfire",
      );
    });

    it("redirects /api/integrations/* to legacy site", () => {
      const response = handleRedirect(
        createRequest("/api/integrations/some-integration"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://legacy.mirascope.com/api/integrations/some-integration",
      );
    });

    it("redirects /docs/mirascope/* to /docs/v1/*", () => {
      const response = handleRedirect(
        createRequest("/docs/mirascope/some-page"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/v1/some-page",
      );
    });

    it("redirects /docs/mirascope/learn/* to /docs/v1/learn/*", () => {
      const response = handleRedirect(
        createRequest("/docs/mirascope/learn/calls"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/v1/learn/calls",
      );
    });

    it("redirects /docs/mirascope/guides/* to /docs/v1/guides/*", () => {
      const response = handleRedirect(
        createRequest("/docs/mirascope/guides/agents/web-search"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/v1/guides/agents/web-search",
      );
    });

    it("redirects /docs/mirascope/api/* to /docs/v1/api/*", () => {
      const response = handleRedirect(
        createRequest("/docs/mirascope/api/call"),
      );

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/docs/v1/api/call",
      );
    });

    it("redirects /post/* to /blog/*", () => {
      const response = handleRedirect(createRequest("/post/some-article"));

      expect(response).not.toBeNull();
      expect(response!.status).toBe(301);
      expect(response!.headers.get("Location")).toBe(
        "https://mirascope.com/blog/some-article",
      );
    });
  });

  describe("non-matching paths", () => {
    it("returns null for /docs/v1/* paths (already migrated)", () => {
      const response = handleRedirect(createRequest("/docs/v1/learn/calls"));

      expect(response).toBeNull();
    });

    it("returns null for root path", () => {
      const response = handleRedirect(createRequest("/"));

      expect(response).toBeNull();
    });

    it("returns null for blog paths", () => {
      const response = handleRedirect(createRequest("/blog/some-post"));

      expect(response).toBeNull();
    });

    it("returns null for cloud paths", () => {
      const response = handleRedirect(createRequest("/cloud/dashboard"));

      expect(response).toBeNull();
    });
  });
});
