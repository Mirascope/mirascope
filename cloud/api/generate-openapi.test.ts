import { describe, it, expect } from "vitest";
import { generateOpenApiSpec } from "@/api/generate-openapi";
import { execSync } from "child_process";
import { readFileSync, unlinkSync, mkdtempSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";

describe("generateOpenApiSpec", () => {
  it("should generate OpenAPI spec with correct structure", () => {
    const spec = generateOpenApiSpec();

    expect(spec).toHaveProperty("info");
    expect(spec.info).toMatchObject({
      title: "Mirascope Cloud API",
      version: "0.1.0",
      description: "Complete API documentation for Mirascope Cloud",
    });
  });

  it("should include all three server configurations", () => {
    const spec = generateOpenApiSpec();

    expect(spec).toHaveProperty("servers");
    expect(spec.servers).toHaveLength(3);

    const serverNames = spec.servers.map(
      (s: { "x-fern-server-name"?: string }) => s["x-fern-server-name"],
    );
    expect(serverNames).toContain("production");
    expect(serverNames).toContain("staging");
    expect(serverNames).toContain("local");
  });

  it("should have production server with correct URL", () => {
    const spec = generateOpenApiSpec();
    const productionServer = spec.servers.find(
      (s: { "x-fern-server-name"?: string }) =>
        s["x-fern-server-name"] === "production",
    );

    expect(productionServer).toMatchObject({
      url: "https://v2.mirascope.com/api/v0",
      description: "Production server",
    });
  });

  it("should have staging server with correct URL", () => {
    const spec = generateOpenApiSpec();
    const stagingServer = spec.servers.find(
      (s: { "x-fern-server-name"?: string }) =>
        s["x-fern-server-name"] === "staging",
    );

    expect(stagingServer).toMatchObject({
      url: "https://staging.mirascope.com/api/v0",
      description: "Staging server",
    });
  });

  it("should have local server with correct URL", () => {
    const spec = generateOpenApiSpec();
    const localServer = spec.servers.find(
      (s: { "x-fern-server-name"?: string }) =>
        s["x-fern-server-name"] === "local",
    );

    expect(localServer).toMatchObject({
      url: "http://localhost:3000/api/v0",
      description: "Local development server",
    });
  });

  it("should include base spec properties from OpenApi.fromApi", () => {
    const spec = generateOpenApiSpec();

    // The spec should have properties from the base OpenAPI spec
    expect(spec).toHaveProperty("openapi");
    expect(spec).toHaveProperty("paths");
  });
});

describe("generate-openapi script execution", () => {
  it("should output JSON when executed as a script", () => {
    // Use file-based approach to avoid buffer truncation issues with execSync
    const tempDir = mkdtempSync(join(tmpdir(), "openapi-test-"));
    const tempFile = join(tempDir, "output.json");

    execSync(`bun generate-openapi.ts > "${tempFile}"`, {
      cwd: __dirname,
      encoding: "utf-8",
    });

    const output = readFileSync(tempFile, "utf-8");
    unlinkSync(tempFile);

    const parsed_stdout = JSON.parse(output) as {
      info?: { title?: string };
    };
    expect(parsed_stdout).toHaveProperty("info");
    expect(parsed_stdout.info).toHaveProperty("title", "Mirascope Cloud API");
  });
});
