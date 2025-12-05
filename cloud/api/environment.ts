import { Context } from "effect";

export class Environment extends Context.Tag("EnvironmentService")<
  Environment,
  { readonly env: string }
>() {}
