import { Context } from "effect";

export type Environment = {
  readonly env: string;
};

export class EnvironmentService extends Context.Tag("EnvironmentService")<
  EnvironmentService,
  Environment
>() {}
