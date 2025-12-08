import { describe, it, expect } from "vitest";
import { Effect } from "effect";
import { withTestClient } from "@/tests/api";
import fs from "fs/promises";
import path from "path";

describe(
  "OpenAPI Docs API",
  withTestClient(async (client) => {
    it("GET /openapi", async () => {
      const result = await Effect.runPromise(client.docs.openapi());

      const openApiPath = path.resolve(process.cwd(), "../fern/openapi.json");
      const openApiContents = await fs.readFile(openApiPath, "utf8");
      const expectedSpec = JSON.parse(openApiContents);

      expect(result).toEqual(expectedSpec);
    });
  }),
);
