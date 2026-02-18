/**
 * Agent configuration via Effect Config.
 */
import { Config, Context, Effect, Layer } from "effect";

export interface AgentConfig {
  readonly authToken: string;
  readonly port: number;
  readonly tunnelConfigPath: string;
  readonly tunnelName: string;
  readonly tunnelHostnameSuffix: string;
  readonly maxClaws: number;
  readonly portRangeStart: number;
  readonly portRangeEnd: number;
}

export class AgentConfigService extends Context.Tag("AgentConfig")<
  AgentConfigService,
  AgentConfig
>() {}

export const AgentConfigLive = Layer.effect(
  AgentConfigService,
  Effect.gen(function* () {
    const authToken = yield* Config.string("MAC_AGENT_AUTH_TOKEN").pipe(
      Config.withDefault("changeme"),
    );
    const port = yield* Config.integer("MAC_AGENT_PORT").pipe(
      Config.withDefault(7600),
    );
    const tunnelConfigPath = yield* Config.string(
      "MAC_AGENT_TUNNEL_CONFIG",
    ).pipe(Config.withDefault("/etc/cloudflared/config.yml"));
    const tunnelName = yield* Config.string("MAC_AGENT_TUNNEL_NAME").pipe(
      Config.withDefault("local-william"),
    );
    const tunnelHostnameSuffix = yield* Config.string(
      "MAC_AGENT_TUNNEL_SUFFIX",
    ).pipe(Config.withDefault("claws.mirascope.dev"));
    const maxClaws = yield* Config.integer("MAC_AGENT_MAX_CLAWS").pipe(
      Config.withDefault(12),
    );
    const portRangeStart = yield* Config.integer(
      "MAC_AGENT_PORT_RANGE_START",
    ).pipe(Config.withDefault(3001));
    const portRangeEnd = yield* Config.integer(
      "MAC_AGENT_PORT_RANGE_END",
    ).pipe(Config.withDefault(3100));

    return {
      authToken,
      port,
      tunnelConfigPath,
      tunnelName,
      tunnelHostnameSuffix,
      maxClaws,
      portRangeStart,
      portRangeEnd,
    };
  }),
);
