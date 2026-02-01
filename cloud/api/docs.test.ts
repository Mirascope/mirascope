import { describe, it, expect } from "@effect/vitest";
import { Effect } from "effect";
import fs from "fs/promises";
import path from "path";

import { TestApiClient, TestClient } from "@/tests/api";

describe("OpenAPI Docs API", () => {
  it.effect("GET /openapi", () =>
    Effect.gen(function* () {
      const client = yield* TestApiClient;
      const result = (yield* client.docs.openapi()) as unknown;

      const openApiPath = path.resolve(process.cwd(), "../fern/openapi.json");
      const openApiContents = yield* Effect.promise(() =>
        fs.readFile(openApiPath, "utf8"),
      );
      const expectedSpec = JSON.parse(openApiContents) as unknown;

      expect(result).toEqual(expectedSpec);
    }).pipe(Effect.provide(TestClient.Default)),
  );
});
