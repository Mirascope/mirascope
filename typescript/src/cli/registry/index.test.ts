import { describe, expect, it } from "vitest";

import { RegistryClient } from "@/cli/registry";

describe("registry index exports", () => {
  it("exports RegistryClient", () => {
    expect(RegistryClient).toBeDefined();
    expect(typeof RegistryClient).toBe("function");
  });
});
