import { router as healthRouter } from "./health";
import { router as tracesRouter } from "./traces";

export const router = {
  traces: tracesRouter,
  health: healthRouter,
};
