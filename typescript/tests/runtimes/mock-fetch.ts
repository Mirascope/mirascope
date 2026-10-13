/**
 * Cross-runtime fetch mock for runtime integration tests.
 *
 * Replaces globalThis.fetch with a mock that serves canned responses
 * from cassette JSON files. If a cassette is missing, the real fetch
 * is used and the response is saved to disk (record-if-missing).
 *
 * Works in Node.js, Bun, and Deno.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const cassettesDir = join(__dirname, "cassettes");

const CASSETTE_NAMES = ["tool-call.json", "text-response.json"] as const;

function cassettePath(name: string): string {
  return join(cassettesDir, name);
}

function loadCassette(name: string): unknown | null {
  const path = cassettePath(name);
  if (existsSync(path)) {
    return JSON.parse(readFileSync(path, "utf-8"));
  }
  return null;
}

function saveCassette(name: string, data: unknown): void {
  mkdirSync(cassettesDir, { recursive: true });
  writeFileSync(cassettePath(name), JSON.stringify(data, null, 2) + "\n");
}

interface MockRequestTool {
  name: string;
  description?: string;
  input_schema: {
    type: string;
    properties?: Record<string, unknown>;
    required?: string[];
  };
}

export interface MockRequestBody {
  model?: string;
  messages?: unknown[];
  tools?: MockRequestTool[];
  [k: string]: unknown;
}

export interface MockFetchState {
  requests: Array<{ url: string; body: MockRequestBody | null }>;
}

/**
 * Install a mock fetch that returns canned Anthropic API responses.
 *
 * First call returns the tool-call cassette (tool_use response).
 * Second call returns the text-response cassette (end_turn response).
 *
 * If a cassette file is missing, the real fetch is called, the response
 * is saved to disk, and returned — matching Polly.js's recordIfMissing.
 */
export function installMockFetch(): MockFetchState {
  const responses = CASSETTE_NAMES.map(loadCassette);
  const originalFetch = globalThis.fetch;

  const state: MockFetchState = { requests: [] };
  let callIndex = 0;

  globalThis.fetch = (async (
    input: string | URL | Request,
    init?: RequestInit,
  ): Promise<Response> => {
    const url =
      typeof input === "string"
        ? input
        : input instanceof URL
          ? input.toString()
          : input.url;

    let body: MockRequestBody | null = null;
    if (init?.body) {
      body = JSON.parse(
        typeof init.body === "string"
          ? init.body
          : new TextDecoder().decode(init.body as ArrayBuffer),
      ) as MockRequestBody;
    }

    state.requests.push({ url, body });

    const idx = callIndex++;
    const cassetteName = CASSETTE_NAMES[idx];
    if (!cassetteName) {
      throw new Error(
        `mock-fetch: No cassette mapped for request #${idx + 1} to ${url}`,
      );
    }

    const canned = responses[idx];
    if (canned !== null) {
      return new Response(JSON.stringify(canned), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }

    // Record-if-missing: pass through to real fetch, save response
    console.log(`[mock-fetch] Recording missing cassette: ${cassetteName}`);
    const realResponse = await originalFetch(input, init);
    const responseBody = await realResponse.json();
    saveCassette(cassetteName, responseBody);
    responses[idx] = responseBody;

    return new Response(JSON.stringify(responseBody), {
      status: realResponse.status,
      headers: { "content-type": "application/json" },
    });
  }) as typeof fetch;

  return state;
}
