/**
 * Effect + TanStack Query integration via effect-query.
 * @see https://github.com/voidhashcom/effect-query
 */

import { Effect } from "effect";
import { HttpApiClient } from "@effect/platform";
import { BrowserHttpClient } from "@effect/platform-browser";
import { createEffectQuery } from "effect-query";
import { MirascopeCloudApi } from "@/api/api";

export class ApiClient extends Effect.Service<ApiClient>()("ApiClient", {
  dependencies: [BrowserHttpClient.layerXMLHttpRequest],
  effect: HttpApiClient.make(MirascopeCloudApi, { baseUrl: "/api/v0" }),
}) {}

/**
 * @example
 * eq.queryOptions({
 *   queryKey: ["organizations"],
 *   queryFn: () => Effect.gen(function* () {
 *     const client = yield* ApiClient;
 *     return yield* client.organizations.list();
 *   }),
 * })
 */
export const eq = createEffectQuery(ApiClient.Default);
