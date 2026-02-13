# BYOK (Bring Your Own Key) — Design Document

## Problem

Users on Pro/Team plans want to use their own API keys for LLM providers, avoiding Mirascope billing and using their own rate limits/quotas. Currently, all router requests use Mirascope-managed keys and are billed through our credit system. BYOK allows eligible users to bypass this billing while still benefiting from our observability and routing infrastructure.

## Supported Providers

- `anthropic`
- `openai`
- `google`

These match the current router providers defined in `cloud/api/router/providers.ts`.

## Architecture

### 1. Database

New `project_api_keys` table:

| Column         | Type      | Description                                          |
| -------------- | --------- | ---------------------------------------------------- |
| `id`           | `uuid`    | Primary key                                          |
| `projectId`    | `uuid`    | FK → `projects.id`                                   |
| `provider`     | `text`    | Enum: `anthropic` \| `openai` \| `google`            |
| `encryptedKey` | `text`    | AES-256-GCM encrypted API key                        |
| `nonce`        | `text`    | Nonce/IV for AES-GCM decryption                      |
| `keyPrefix`    | `text`    | Last 4 characters of the key (for display)           |
| `createdAt`    | `timestamp` | Row creation time                                  |
| `updatedAt`    | `timestamp` | Last update time                                   |

**Constraints:**

- Unique constraint on `(projectId, provider)` — one key per provider per project
- Foreign key on `projectId` with `CASCADE` delete (keys removed when project is deleted)

**Encryption:** AES-256-GCM, matching the existing pattern in `cloud/claws/crypto.ts` used for gateway token encryption.

### 2. Service Layer (Effect)

New `ProjectApiKeys` service following the existing `BaseAuthenticatedEffectService` pattern.

**Methods:**

- `set(projectId, provider, key)` — Encrypt the key using AES-256-GCM, extract last 4 chars, and upsert into `project_api_keys`. Returns `{ provider, lastFour, updatedAt }`.
- `get(projectId, provider)` — Decrypt and return the plaintext key. Used only internally by the router at proxy time. Never exposed via API.
- `delete(projectId, provider)` — Remove the stored key for the given provider.
- `list(projectId)` — Return metadata for all stored keys: `{ provider, lastFour, updatedAt }[]`. Never returns key values.

**Permissions:**

- All methods require project `ADMIN` role
- Org `OWNER`/`ADMIN` have implicit access through existing role hierarchy

### 3. Router Integration

In `cloud/app/routes/router.v2.$provider.$.tsx`, after authentication:

```
1. Authenticate request (existing flow)
2. Resolve project + provider from route params
3. Check org plan tier:
   - Free tier → skip BYOK, use existing Mirascope-key flow
   - Pro/Team tier → proceed to BYOK check
4. Query project_api_keys for (projectId, provider):
   - Key found → BYOK path:
     a. Use decrypted key for proxyToProvider
     b. Skip reserveRouterFunds (no billing)
     c. Skip metering / cost calculation
     d. Log request with byok: true flag for analytics
   - No key found → existing flow:
     a. Use Mirascope-managed key
     b. reserveRouterFunds + metering as usual
```

**Cache strategy:**

- Cache plan tier + BYOK key existence per `(projectId, provider)` with short TTL (~60s)
- On key set/delete, invalidate the cache entry for that `(projectId, provider)`
- Decrypted key values should NOT be cached — decrypt on each request for security
- Plan tier can be cached more aggressively since it changes rarely

### 4. API Endpoints

#### `PUT /api/projects/:projectId/api-keys/:provider`

Set or update a BYOK key for a provider.

- **Body:** `{ key: string }`
- **Validation:** `provider` must be one of `anthropic | openai | google`
- **Auth:** Project ADMIN + Pro/Team plan
- **Response:** `{ provider, lastFour, updatedAt }`

#### `DELETE /api/projects/:projectId/api-keys/:provider`

Remove a stored BYOK key.

- **Auth:** Project ADMIN + Pro/Team plan
- **Response:** `204 No Content`

#### `GET /api/projects/:projectId/api-keys`

List all providers with BYOK keys configured.

- **Auth:** Project ADMIN + Pro/Team plan
- **Response:** `{ provider, lastFour, updatedAt }[]`
- **Note:** Never returns the full key value

### 5. UI

New "API Keys" section in the project settings page.

**Layout:**

- Per-provider row showing:
  - Provider name + icon (Anthropic, OpenAI, Google)
  - Status: "Not configured" or masked display showing `••••{lastFour}`
  - Last updated timestamp (if configured)
  - Actions: "Set Key" button (opens modal with password input) / "Clear" button (with confirmation)

**Plan gating:**

- Free tier users see the section with an upgrade prompt: "Upgrade to Pro to use your own API keys"
- Pro/Team users see the full management UI

**Key input modal:**

- Password-type input field (masked by default)
- Toggle to reveal key while typing
- "Save" submits to PUT endpoint
- Success toast with provider name

### 6. Billing

**BYOK requests:**

- No fund reservation (`reserveRouterFunds` skipped)
- No metering or cost calculation
- No charges applied

**Analytics:**

- Router requests are still logged with a `byok: true` flag
- Usage is tracked for display/analytics purposes but not billed
- This enables dashboards showing BYOK vs billed request volume

## Security

- **Encryption at rest:** Keys encrypted with AES-256-GCM using the same crypto infrastructure as gateway tokens (`cloud/claws/crypto.ts`)
- **No full key exposure:** API never returns the full key — only last 4 characters for display
- **Decrypt only at proxy time:** Keys are decrypted in the router handler only when proxying a request, and the plaintext is not persisted or cached
- **Plan tier gating:** Free tier users cannot set BYOK keys, preventing abuse of the feature to bypass billing
- **Admin-only access:** Only project admins can manage keys, limiting the blast radius of compromised accounts

## Migration

New Drizzle migration for the `project_api_keys` table:

```sql
CREATE TABLE "project_api_keys" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "project_id" uuid NOT NULL REFERENCES "projects"("id") ON DELETE CASCADE,
  "provider" text NOT NULL,
  "encrypted_key" text NOT NULL,
  "nonce" text NOT NULL,
  "key_prefix" text NOT NULL,
  "created_at" timestamp DEFAULT now() NOT NULL,
  "updated_at" timestamp DEFAULT now() NOT NULL,
  CONSTRAINT "project_api_keys_project_id_provider_unique" UNIQUE("project_id", "provider")
);
```

## Open Questions

1. **Custom base URLs:** Should we support custom base URLs per provider (e.g., for Azure OpenAI, AWS Bedrock endpoints) in the future? This would require an additional `baseUrl` column.

2. **Key rotation:** Should we support versioned keys or just overwrite? Current design overwrites on upsert. Versioning would add complexity but enable rollback.

3. **Scope — org vs project level:** Starting with project-level keys per William's direction. Org-level keys could be a future enhancement where a single key applies to all projects in an org unless overridden at the project level.

4. **Key validation:** Should we validate keys against the provider API on set (e.g., make a lightweight API call to verify the key works)? This adds latency to the set operation but catches typos immediately.

5. **Error handling for invalid BYOK keys:** When a BYOK key is rejected by the provider at proxy time, should we surface a specific error to the user? Should we auto-disable the key after N consecutive failures?
