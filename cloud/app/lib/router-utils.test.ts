import { describe, it, expect } from "vitest";
import { isHiddenRoute } from "./hidden-routes";

describe("isHiddenRoute", () => {
  it("should correctly identify dev routes as hidden", () => {
    // These should all be hidden
    expect(isHiddenRoute("/dev")).toBe(true);
    expect(isHiddenRoute("/dev/")).toBe(true);
    expect(isHiddenRoute("/dev/audit-metadata")).toBe(true);
    expect(isHiddenRoute("/dev/social-card")).toBe(true);
    expect(isHiddenRoute("/dev/some/nested/route")).toBe(true);

    // These should not be hidden
    expect(isHiddenRoute("/developer")).toBe(false);
    expect(isHiddenRoute("/development")).toBe(false);
    expect(isHiddenRoute("/blog/dev-tools")).toBe(false);
    expect(isHiddenRoute("/")).toBe(false);
    expect(isHiddenRoute("/docs/mirascope")).toBe(false);
  });
});
