/**
 * Idempotent seed script for local development.
 *
 * Creates a known dev state:
 * - Dev user (noreply@mirascope.com)
 * - "test-org" organization
 * - "test-claw" claw (status: active)
 * - Auth session (long-lived, used by dev cookie)
 *
 * Safe to re-run — uses upserts / conflict handling.
 *
 * Usage: bun run scripts/dev/seed.ts
 */
import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";

import { claws } from "../../db/schema/claws";
import { organizationMemberships } from "../../db/schema/organization-memberships";
import { organizations } from "../../db/schema/organizations";
import { sessions } from "../../db/schema/sessions";
import { users } from "../../db/schema/users";

// ---------------------------------------------------------------------------
// Known IDs (deterministic so re-runs are idempotent)
// ---------------------------------------------------------------------------

const DEV_USER_ID = "00000000-0000-4000-8000-000000000001";
const DEV_ORG_ID = "00000000-0000-4000-8000-000000000002";
const DEV_CLAW_ID = "00000000-0000-4000-8000-000000000003";
const DEV_SESSION_ID = "00000000-0000-4000-8000-000000000004";

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const DATABASE_URL =
  process.env.DATABASE_URL ??
  "postgres://postgres:postgres@localhost:5432/mirascope_cloud_dev";

async function seed() {
  const sql = postgres(DATABASE_URL, { max: 1 });
  const db = drizzle(sql);

  console.log("🌱 Seeding dev database...");

  // 1. Dev user
  const [user] = await db
    .insert(users)
    .values({
      id: DEV_USER_ID,
      email: "noreply@mirascope.com",
      name: "Dev User",
      accountType: "user",
    })
    .onConflictDoUpdate({
      target: users.id,
      set: { name: "Dev User", email: "noreply@mirascope.com" },
    })
    .returning();
  console.log(`  ✅ User: ${user.email} (${user.id})`);

  // 2. Organization
  const [org] = await db
    .insert(organizations)
    .values({
      id: DEV_ORG_ID,
      name: "Test Org",
      slug: "test-org",
      stripeCustomerId: "cus_dev_test_org_local",
    })
    .onConflictDoUpdate({
      target: organizations.id,
      set: { name: "Test Org", slug: "test-org" },
    })
    .returning();
  console.log(`  ✅ Org: ${org.slug} (${org.id})`);

  // 3. Org membership (owner)
  await db
    .insert(organizationMemberships)
    .values({
      memberId: DEV_USER_ID,
      organizationId: DEV_ORG_ID,
      role: "OWNER",
    })
    .onConflictDoNothing();
  console.log(`  ✅ Membership: Dev User → Mirascope (OWNER)`);

  // 4. Claw
  const [claw] = await db
    .insert(claws)
    .values({
      id: DEV_CLAW_ID,
      slug: "test-claw",
      displayName: "Test Claw",
      description: "Local development claw",
      organizationId: DEV_ORG_ID,
      createdByUserId: DEV_USER_ID,
      status: "active",
      instanceType: "basic",
    })
    .onConflictDoUpdate({
      target: claws.id,
      set: {
        displayName: "Test Claw",
        status: "active",
      },
    })
    .returning();
  console.log(`  ✅ Claw: ${claw.slug} (${claw.id})`);

  // 5. Auth session (expires in 1 year)
  const expiresAt = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000);
  await db
    .insert(sessions)
    .values({
      id: DEV_SESSION_ID,
      userId: DEV_USER_ID,
      expiresAt,
    })
    .onConflictDoUpdate({
      target: sessions.id,
      set: { expiresAt },
    });
  console.log(
    `  ✅ Session: ${DEV_SESSION_ID} (expires ${expiresAt.toISOString()})`,
  );

  console.log("\n🎉 Dev seed complete!");
  console.log(`\n📋 Dev session cookie: session=${DEV_SESSION_ID}`);
  console.log(`   Navigate to: /test-org/claws/test-claw/chat`);

  await sql.end();
}

seed().catch((err) => {
  console.error("❌ Seed failed:", err);
  process.exit(1);
});
