import { OpenAPIHono } from "@hono/zod-openapi";

import type { Environment } from "@/worker/environment";
import { handleTraces } from "./traces/handlers";
import { tracesRoute } from "./traces/routes";

export const apiRouter = new OpenAPIHono<{
  Bindings: Environment;
}>();

// TODO: add API key authentication
apiRouter.openapi(tracesRoute, handleTraces);
