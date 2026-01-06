import fs from "fs";
import { CLICKHOUSE_CONNECTION_FILE } from "@/tests/global-setup";

type ClickHouseConnectionFile = {
  url: string;
  user: string;
  password: string;
  database: string;
  nativePort: number;
};

function applyClickHouseEnvFromFile(): void {
  if (!fs.existsSync(CLICKHOUSE_CONNECTION_FILE)) return;

  const raw = fs.readFileSync(CLICKHOUSE_CONNECTION_FILE, "utf-8");
  const parsed = JSON.parse(raw) as ClickHouseConnectionFile;

  process.env.CLICKHOUSE_URL = parsed.url;
  process.env.CLICKHOUSE_USER = parsed.user;
  process.env.CLICKHOUSE_PASSWORD = parsed.password;
  process.env.CLICKHOUSE_DATABASE = parsed.database;
  process.env.CLICKHOUSE_MIGRATE_NATIVE_PORT = String(parsed.nativePort);
}

applyClickHouseEnvFromFile();
