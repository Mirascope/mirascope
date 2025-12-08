export * from "@/db/schema/sessions";
export * from "@/db/schema/users";

export type { PublicSession } from "@/db/schema/sessions";
export type { PublicUser } from "@/db/schema/users";

import { users } from "@/db/schema/users";
import { sessions } from "@/db/schema/sessions";

export type DatabaseTable = typeof users | typeof sessions;
