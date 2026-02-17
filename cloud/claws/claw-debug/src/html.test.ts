import { describe, expect, test } from "bun:test";
import { buildBootstrapHtml } from "./html";

describe("buildBootstrapHtml", () => {
  test("includes gateway URL", () => {
    const html = buildBootstrapHtml("ws://localhost:18789");
    expect(html).toContain("ws://localhost:18789");
    expect(html).toContain("http://localhost:18789");
    expect(html).toContain("openclaw.control.settings.v1");
  });

  test("includes token when provided", () => {
    const html = buildBootstrapHtml("wss://claw.example.com", "secret");
    expect(html).toContain("secret");
  });

  test("does not include token field when not provided", () => {
    const html = buildBootstrapHtml("ws://localhost:18789");
    expect(html).not.toContain('"token"');
  });

  test("escapes HTML in URLs", () => {
    const html = buildBootstrapHtml("ws://localhost:18789/<b>xss</b>");
    // The display code/href should have escaped HTML
    expect(html).toContain("&lt;b&gt;xss&lt;/b&gt;");
  });
});
