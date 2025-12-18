import { QueryClient } from "@tanstack/react-query";
import { createEffectQuery } from "effect-query";
import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
} from "@effect/platform";
import { Effect, Layer } from "effect";
import { MirascopeCloudApi } from "@/api/api";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: (failureCount, error) => {
        // Don't retry on 401 (auth errors)
        if (error instanceof Error && error.message.includes("401")) {
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});

// Create a fetch-based HttpClient for the browser with credentials
const BrowserHttpClient = HttpClient.make(
  (request: HttpClientRequest.HttpClientRequest) =>
    Effect.gen(function* () {
      const method = request.method.toUpperCase();
      const options: RequestInit = {
        method: request.method,
        headers: request.headers as HeadersInit,
        credentials: "include", // Include cookies for auth
      };

      if (method !== "GET" && method !== "HEAD" && request.body !== undefined) {
        options.body = (request.body.toJSON() as { body: BodyInit }).body;
      }

      const webResponse = yield* Effect.promise(() =>
        fetch(request.url, options),
      );

      return HttpClientResponse.fromWeb(request, webResponse);
    }),
);

const BrowserHttpClientLayer = Layer.succeed(
  HttpClient.HttpClient,
  BrowserHttpClient,
);

// Create ApiClient service that provides the typed HttpApiClient
export class ApiClient extends Effect.Service<ApiClient>()("ApiClient", {
  dependencies: [BrowserHttpClientLayer],
  scoped: HttpApiClient.make(MirascopeCloudApi, {
    baseUrl: "/api/v0",
  }),
}) {}

// Create the effect-query instance with our ApiClient layer
export const eq = createEffectQuery(ApiClient.Default);
