/**
 * Agent configuration via Effect Config.
 */
import { Context, Effect, Layer } from "effect";

export interface AgentConfig {
  readonly authToken: string;
  readonly port: number;
  readonly tunnelConfigPath: string;
  readonly tunnelHostnameSuffix: string;
  readonly maxClaws: number;
  readonly portRangeStart: number;
  readonly portRangeEnd: number;
}

export class Config extends Context.Tag("MiniAgent/Config")<
  Config,
  AgentConfig
>() {}

export const ConfigLive = Layer.effect(
  Config,
  Effect.sync(() => {
    const authToken = process.env.AGENT_AUTH_TOKEN ?? process.env.AGENT_TOKEN;
    if (!authToken) {
      throw new Error(
        "AGENT_AUTH_TOKEN or AGENT_TOKEN environment variable is required",
      );
    }

    return {
      authToken,
      port: parseInt(process.env.AGENT_PORT ?? "7600", 10),
      tunnelConfigPath:
        process.env.TUNNEL_CONFIG_PATH ?? "/etc/cloudflared/config.yml",
      tunnelHostnameSuffix:
        process.env.TUNNEL_HOSTNAME_SUFFIX ?? "claws.mirascope.dev",
      maxClaws: parseInt(process.env.MAX_CLAWS ?? "12", 10),
      portRangeStart: parseInt(process.env.PORT_RANGE_START ?? "3001", 10),
      portRangeEnd: parseInt(process.env.PORT_RANGE_END ?? "3100", 10),
    };
  }),
);
