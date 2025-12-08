import { Effect } from "effect";
import { MirascopeCloudApi } from "@/api/router";
import {
  HttpClient,
  HttpApiClient,
  HttpClientRequest,
  HttpClientResponse,
} from "@effect/platform";
import { Layer } from "effect";
import { getWebHandler } from "@/api/handler";

function createHandlerHttpClient(webHandler: ReturnType<typeof getWebHandler>) {
  return HttpClient.make((request: HttpClientRequest.HttpClientRequest) =>
    Effect.gen(function* () {
      const url = new URL(request.url);
      const method = request.method.toUpperCase();
      const options: RequestInit = {
        method: request.method,
        headers: request.headers,
      };

      if (method !== "GET" && method !== "HEAD" && request.body !== undefined) {
        options.body = (request.body.toJSON() as { body: BodyInit }).body;
      }

      const webResponse = yield* Effect.promise(() =>
        webHandler.handler(new Request(url.toString(), options)),
      );

      return HttpClientResponse.fromWeb(request, webResponse);
    }),
  );
}

function createTestClient() {
  const webHandler = getWebHandler({ environment: "test" });
  const HandlerHttpClient = createHandlerHttpClient(webHandler);
  const HandlerHttpClientLayer = Layer.succeed(
    HttpClient.HttpClient,
    HandlerHttpClient,
  );

  return Effect.runSync(
    Effect.scoped(
      HttpApiClient.make(MirascopeCloudApi, {
        // NOTE: no prefix here because we're testing with the web handler directly (no prefix handling required)
        baseUrl: "http://127.0.0.1:3000/",
      }).pipe(Effect.provide(HandlerHttpClientLayer)),
    ),
  );
}

export const withTestClient = (
  testFn: (
    client: Awaited<ReturnType<typeof createTestClient>>,
  ) => void | Promise<void>,
) => {
  return async () => {
    const client = createTestClient();
    await testFn(client);
  };
};
