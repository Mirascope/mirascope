/**
 * CLI argument parsing — zero dependencies.
 */

export interface ParsedArgs {
  gateway: string;
  token?: string;
  port?: number;
  open: boolean;
  help: boolean;
}

const DEFAULT_GATEWAY = "ws://localhost:18789";

export function parseArgs(argv: string[]): ParsedArgs {
  const args: ParsedArgs = {
    gateway: DEFAULT_GATEWAY,
    open: true,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case "--gateway":
        args.gateway = requireValue(argv, ++i, "--gateway");
        break;
      case "--token":
        args.token = requireValue(argv, ++i, "--token");
        break;
      case "--port":
        args.port = parseInt(requireValue(argv, ++i, "--port"), 10);
        if (isNaN(args.port) || args.port < 0 || args.port > 65535) {
          throw new Error("--port must be a valid port number (0-65535)");
        }
        break;
      case "--no-open":
        args.open = false;
        break;
      case "--help":
      case "-h":
        args.help = true;
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }
  }

  // Validate gateway URL
  if (!args.help) {
    try {
      const url = new URL(args.gateway);
      if (!["ws:", "wss:"].includes(url.protocol)) {
        throw new Error(
          `Gateway URL must use ws:// or wss:// protocol, got: ${url.protocol}`,
        );
      }
    } catch (e: any) {
      if (e.message.includes("protocol")) throw e;
      throw new Error(`Invalid gateway URL: ${args.gateway}`);
    }
  }

  return args;
}

function requireValue(argv: string[], i: number, flag: string): string {
  if (i >= argv.length || argv[i].startsWith("--")) {
    throw new Error(`${flag} requires a value`);
  }
  return argv[i];
}
