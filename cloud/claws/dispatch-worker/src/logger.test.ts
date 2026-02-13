import { describe, it, expect, vi, beforeEach } from "vitest";

import { createLogger, redactUrl, summarizeEnvKeys } from "./logger";

describe("createLogger", () => {
  beforeEach(() => {
    vi.spyOn(console, "log").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  it("prefixes with clawId (first 8 chars)", () => {
    const log = createLogger({ clawId: "abcdefgh-1234-5678" });
    log.info("req", "test message");
    expect(console.log).toHaveBeenCalledWith("[abcdefgh] [req] test message");
  });

  it("uses [------] when no clawId", () => {
    const log = createLogger();
    log.info("req", "test");
    expect(console.log).toHaveBeenCalledWith("[------] [req] test");
  });

  it("suppresses debug messages when debug=false", () => {
    const log = createLogger({ clawId: "test1234", debug: false });
    const callsBefore = (console.log as ReturnType<typeof vi.fn>).mock.calls
      .length;
    log.debug("ws", "hidden");
    const callsAfter = (console.log as ReturnType<typeof vi.fn>).mock.calls
      .length;
    expect(callsAfter).toBe(callsBefore);
  });

  it("logs debug messages when debug=true", () => {
    const log = createLogger({ clawId: "test1234", debug: true });
    log.debug("ws", "visible");
    expect(console.log).toHaveBeenCalledWith("[test1234] [ws:debug] visible");
  });

  it("error uses console.error", () => {
    const log = createLogger({ clawId: "test1234" });
    log.error("gateway", "something broke");
    expect(console.error).toHaveBeenCalledWith(
      "[test1234] [gateway] something broke",
    );
  });

  it("passes extra args through", () => {
    const log = createLogger({ clawId: "test1234" });
    const extra = { foo: "bar" };
    log.info("http", "details:", extra);
    expect(console.log).toHaveBeenCalledWith(
      "[test1234] [http] details:",
      extra,
    );
  });
});

describe("redactUrl", () => {
  it("redacts the token parameter", () => {
    const url = new URL("wss://example.com/ws?token=secret123&other=ok");
    expect(redactUrl(url)).toBe("wss://example.com/ws?token=***&other=ok");
  });

  it("returns unchanged URL when no token param", () => {
    const url = new URL("https://example.com/api?foo=bar");
    expect(redactUrl(url)).toBe("https://example.com/api?foo=bar");
  });
});

describe("summarizeEnvKeys", () => {
  it("lists keys and count", () => {
    expect(summarizeEnvKeys({ A: "1", B: "2" })).toBe("2 keys: [A, B]");
  });

  it("handles empty env", () => {
    expect(summarizeEnvKeys({})).toBe("0 keys: []");
  });
});
