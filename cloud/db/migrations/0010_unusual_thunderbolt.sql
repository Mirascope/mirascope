CREATE TABLE "google_workspace_connections" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"claw_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"encrypted_refresh_token" text NOT NULL,
	"refresh_token_key_id" text NOT NULL,
	"scopes" text NOT NULL,
	"connected_email" text NOT NULL,
	"token_expires_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "google_workspace_connections_claw_id_unique" UNIQUE("claw_id")
);
--> statement-breakpoint
ALTER TABLE "google_workspace_connections" ADD CONSTRAINT "google_workspace_connections_claw_id_claws_id_fk" FOREIGN KEY ("claw_id") REFERENCES "public"."claws"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "google_workspace_connections" ADD CONSTRAINT "google_workspace_connections_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;