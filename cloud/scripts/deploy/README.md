# Dev Deploy Scripts

Scripts for deploying the Mirascope dev environment on Cloudflare.

## `dev-reset.ts`

One-command dev environment reset. Run with `bun` from the `cloud/` directory:

```bash
bun scripts/deploy/dev-reset.ts              # Print help
bun scripts/deploy/dev-reset.ts --full       # Drop DB → migrate → build → deploy all (~3 min)
bun scripts/deploy/dev-reset.ts --deploy-only    # Build + deploy both workers (~2 min)
bun scripts/deploy/dev-reset.ts --dispatch-only  # Deploy dispatch worker only (~30s)
```

### Prerequisites

1. **wrangler authenticated**: `npx wrangler whoami`
2. **bun** installed
3. **`cloud/.env.local`** with required env vars (see below)
4. **Secrets** already uploaded to the dev workers (one-time setup)

### `cloud/.env.local`

The script loads all `KEY=VALUE` pairs from `cloud/.env.local`. Required vars:

```bash
# For --full mode (DB reset)
DATABASE_URL=postgres://...

# For --deploy-only / --full (Vite build — these are publishable client-side keys)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
VITE_POSTHOG_HOST=https://us.i.posthog.com
VITE_POSTHOG_API_KEY=phc_...
VITE_GOOGLE_ANALYTICS_MEASUREMENT_ID=G-...
```

Env vars already set in the shell take precedence over `.env.local`.

### How `--env dev` works

Both workers use Cloudflare's `--env dev` flag:

- **Cloud Worker**: The Vite build outputs `dist/server/wrangler.json` with a `configPath` pointing back to `wrangler.jsonc`. Wrangler follows this reference to resolve the `dev` environment block (routes, hyperdrive, vars, etc.). Same mechanism CI uses for `--env staging`.
- **Dispatch Worker**: Direct `--config wrangler.jsonc --env dev`. No Vite involved.

### DB reset

`--full` mode drops and recreates the `public` schema using the `postgres` npm package (already in `cloud/` dependencies), then runs `bun run db:migrate` to apply all drizzle migrations.

**Safety**: Prompts for confirmation before dropping. The `DATABASE_URL` should point to the dev database only.

### Secrets

Cloud Worker secrets are uploaded once and persist across deploys. The dispatch worker secrets (CF_ACCOUNT_ID, CLOUDFLARE_ACCOUNT_ID, SITE_URL) are set idempotently on every run.

For Cloud Worker secrets, use:
```bash
echo "VALUE" | npx wrangler secret put SECRET_NAME --env dev
```

### Dev URLs

- Cloud Worker: https://dev.mirascope.com
- Dispatch Worker: https://openclaw.dev.mirascope.com
- OAuth: Reuses staging OAuth apps ([#2696](https://github.com/Mirascope/mirascope/issues/2696))
