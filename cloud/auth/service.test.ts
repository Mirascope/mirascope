import { describe, it, expect } from "vitest";

import { createAuthService } from "@/auth/service";

describe("createAuthService", () => {
  it("should return an auth service object with all OAuth functions", () => {
    const authService = createAuthService();

    expect(authService).toBeDefined();
    expect(typeof authService.createGitHubProvider).toBe("object"); // Effect
    expect(typeof authService.createGoogleProvider).toBe("object"); // Effect
    expect(typeof authService.initiateOAuth).toBe("function");
    expect(typeof authService.handleCallback).toBe("function");
    expect(typeof authService.handleProxyCallback).toBe("function");
  });
});
