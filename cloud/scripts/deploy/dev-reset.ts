#!/usr/bin/env bun
/**
 * dev-reset.ts — Wipe, rebuild, and redeploy the Mirascope dev environment.
 *
 * Usage:
 *   bun scripts/deploy/dev-reset.ts                  Print this help
 *   bun scripts/deploy/dev-reset.ts --full           Full reset: wipe DB → migrate → build → deploy all
 *   bun scripts/deploy/dev-reset.ts --deploy-only    Build + deploy both workers (skip DB)
 *   bun scripts/deploy/dev-reset.ts --dispatch-only  Deploy only the dispatch worker (~30s)
 *
 * Prerequisites:
 *   - wrangler authenticated (npx wrangler whoami)
 *   - bun installed
 *   - DATABASE_URL in cloud/.env.local (for --full)
 */

import { $ } from "bun";
import { existsSync } from "fs";
import { readFileSync } from "fs";
import { resolve, dirname } from "path";

// ── Config ──────────────────────────────────────────────────────────────────

const CLOUDFLARE_ACCOUNT_ID =
  process.env.CLOUDFLARE_ACCOUNT_ID ?? "0257b70c7de82086ddc4e3480b0202e9";
process.env.CLOUDFLARE_ACCOUNT_ID = CLOUDFLARE_ACCOUNT_ID;

const SCRIPT_DIR = dirname(new URL(import.meta.url).pathname);
const CLOUD_DIR = resolve(SCRIPT_DIR, "../..");
const DISPATCH_DIR = resolve(CLOUD_DIR, "claws/dispatch-worker");

const CLOUD_URL = "https://dev.mirascope.com";
const DISPATCH_URL = "https://openclaw.dev.mirascope.com";

// ── Helpers ─────────────────────────────────────────────────────────────────

const log = (msg: string) => console.log(`──── ${msg}`);
const ok = (msg: string) => console.log(`  ✅ ${msg}`);
const skip = (msg: string) => console.log(`  ⏭️  ${msg}`);
const fail = (msg: string): never => {
  console.error(`  ❌ ${msg}`);
  process.exit(1);
};

function showHelp(): never {
  console.log(`
dev-reset.ts — Wipe, rebuild, and redeploy the Mirascope dev environment.

Usage:
  bun scripts/deploy/dev-reset.ts                  Print this help
  bun scripts/deploy/dev-reset.ts --full           Full reset: wipe DB → migrate → build → deploy all
  bun scripts/deploy/dev-reset.ts --deploy-only    Build + deploy both workers (skip DB)
  bun scripts/deploy/dev-reset.ts --dispatch-only  Deploy only the dispatch worker (~30s)
`);
  process.exit(0);
}

/** Load all KEY=VALUE pairs from cloud/.env.local into process.env (if not already set). */
function loadEnvLocal(): void {
  const envLocal = resolve(CLOUD_DIR, ".env.local");
  if (!existsSync(envLocal)) return;

  const content = readFileSync(envLocal, "utf-8");
  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq < 0) continue;
    const key = trimmed.slice(0, eq);
    const value = trimmed.slice(eq + 1);
    if (!process.env[key]) process.env[key] = value;
  }
}

function requireEnv(name: string): string {
  const value = process.env[name];
  if (value) return value;
  return fail(`${name} not set. Add it to cloud/.env.local or export it.`);
}

async function confirm(prompt: string): Promise<boolean> {
  process.stdout.write(`  ${prompt} [y/N] `);
  for await (const line of console) {
    return line.trim().toLowerCase() === "y";
  }
  return false;
}

// ── Parse args ──────────────────────────────────────────────────────────────

type Mode = "full" | "deploy" | "dispatch";

const args = process.argv.slice(2);
let mode: Mode | null = null;

for (const arg of args) {
  switch (arg) {
    case "--full":
      mode = "full";
      break;
    case "--deploy-only":
      mode = "deploy";
      break;
    case "--dispatch-only":
      mode = "dispatch";
      break;
    case "-h":
    case "--help":
      showHelp();
      break; // unreachable — showHelp() is never
    default:
      fail(`Unknown flag: ${arg}`);
  }
}

if (!mode) showHelp();

// ── Load .env.local ─────────────────────────────────────────────────────────

loadEnvLocal();

// ── Preflight ───────────────────────────────────────────────────────────────

log("Preflight");

if (!existsSync(resolve(CLOUD_DIR, "package.json")))
  fail(`No package.json in ${CLOUD_DIR}`);
if (!existsSync(resolve(DISPATCH_DIR, "wrangler.jsonc")))
  fail("Dispatch worker config missing");

try {
  await $`npx wrangler whoami`.quiet();
} catch {
  fail("wrangler not authenticated — run: npx wrangler login");
}

ok("Ready");

// ── Step 1: Database reset ──────────────────────────────────────────────────

if (mode === "full") {
  log("Step 1: Database reset");

  const databaseUrl = requireEnv("DATABASE_URL");
  const masked = databaseUrl.replace(/:\/\/[^@]+@/, "://****@");
  console.log(`  DB: ${masked}`);

  console.log("  Dropping schema...");
  const postgres = (await import("postgres")).default;
  const sql = postgres(databaseUrl);
  await sql`DROP SCHEMA public CASCADE`;
  await sql`DROP SCHEMA IF EXISTS drizzle CASCADE`;
  await sql`CREATE SCHEMA public`;
  await sql`GRANT ALL ON SCHEMA public TO public`;
  await sql.end();
  ok("Schema dropped and recreated (including drizzle migration state)");

  // Verify DB is accessible before running migrations
  const verify = postgres(databaseUrl);
  const [{ current_schema }] = await verify`SELECT current_schema`;
  console.log(`  Schema: ${current_schema}`);
  await verify.end();

  console.log("  Running migrations...");
  await $`cd ${CLOUD_DIR} && DATABASE_URL=${databaseUrl} bun run db:migrate`;

  // Verify tables exist after migration
  const check = (await import("postgres")).default(databaseUrl);
  const tables = await check`
    SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename
  `;
  await check.end();
  if (tables.length === 0) {
    fail(
      "Migrations ran but no tables exist! Check drizzle.config.ts and migration files.",
    );
  }
  console.log(
    `  Tables: ${tables.map((t: { tablename: string }) => t.tablename).join(", ")}`,
  );
  ok("Migrations applied");

  // Seed dev data (same IDs as scripts/dev/seed.ts + staging.ts auto-auth)
  console.log("  Seeding dev data...");
  await $`cd ${CLOUD_DIR} && DATABASE_URL=${databaseUrl} bun run scripts/dev/seed.ts`;
  ok("Dev data seeded (test user + test-org + session)");
} else {
  skip("Step 1: Database (use --full to reset)");
}

// ── Steps 2-4: Build + deploy Cloud Worker ──────────────────────────────────

if (mode !== "dispatch") {
  log("Step 2: Ensure Cloudflare Queues exist");
  const QUEUES = [
    "router-metering-dev",
    "spans-ingest-dev",
    "router-metering-dlq-dev",
    "spans-ingest-dlq-dev",
  ];
  for (const q of QUEUES) {
    try {
      await $`npx wrangler queues create ${q}`.quiet();
      console.log(`  ✅ Created queue: ${q}`);
    } catch {
      console.log(`  ⏭️  Queue already exists: ${q}`);
    }
  }
  ok("Queues ready");

  log("Step 3: Build Cloud Worker");
  // VITE_* vars must be set at build time — Vite bakes them into the client bundle.
  // These are loaded from .env.local (or environment). They're publishable/client-side keys.
  const VITE_STRIPE = requireEnv("VITE_STRIPE_PUBLISHABLE_KEY");
  const VITE_PH_HOST = requireEnv("VITE_POSTHOG_HOST");
  const VITE_PH_KEY = requireEnv("VITE_POSTHOG_API_KEY");
  const VITE_GA = requireEnv("VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID");
  await $`cd ${CLOUD_DIR} && CLOUDFLARE_ENV=dev VITE_STRIPE_PUBLISHABLE_KEY=${VITE_STRIPE} VITE_POSTHOG_HOST=${VITE_PH_HOST} VITE_POSTHOG_API_KEY=${VITE_PH_KEY} VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID=${VITE_GA} bun run build`;
  ok("Built → dist/");

  log("Step 4: Deploy Cloud Worker");
  await $`cd ${CLOUD_DIR} && npx wrangler deploy --env dev`;
  ok(`Deployed → ${CLOUD_URL}`);

  skip("Step 5: Secrets managed separately (see README)");
} else {
  skip("Steps 2-5: Cloud Worker (--dispatch-only)");
}

// ── Step 6: Deploy Dispatch Worker ──────────────────────────────────────────

log("Step 6: Deploy Dispatch Worker");
await $`cd ${DISPATCH_DIR} && npx wrangler deploy --env dev --config wrangler.jsonc`;
ok(`Deployed → ${DISPATCH_URL}`);

// ── Step 6: Dispatch Worker secrets ─────────────────────────────────────────

log("Step 6: Dispatch Worker secrets");
const secretCmd = (name: string, value: string) =>
  $`echo ${value} | npx wrangler secret put ${name} --env dev --config ${resolve(DISPATCH_DIR, "wrangler.jsonc")}`.quiet();

await secretCmd("CLOUDFLARE_ACCOUNT_ID", CLOUDFLARE_ACCOUNT_ID);
await secretCmd("CLOUDFLARE_ACCOUNT_ID", CLOUDFLARE_ACCOUNT_ID);
await secretCmd("SITE_URL", DISPATCH_URL);
ok("Secrets set");

// ── Done ────────────────────────────────────────────────────────────────────

console.log();
log("🎉 Dev environment ready!");
console.log(`  Cloud:    ${CLOUD_URL}`);
console.log(`  Dispatch: ${DISPATCH_URL}`);
console.log(`  Test:     open ${CLOUD_URL} (OAuth → staging)`);
