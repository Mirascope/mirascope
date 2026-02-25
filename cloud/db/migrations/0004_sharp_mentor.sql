ALTER TABLE "organizations" ADD COLUMN "auto_reload_enabled" boolean DEFAULT false NOT NULL;--> statement-breakpoint
ALTER TABLE "organizations" ADD COLUMN "auto_reload_threshold_centicents" bigint DEFAULT 0 NOT NULL;--> statement-breakpoint
ALTER TABLE "organizations" ADD COLUMN "auto_reload_amount_centicents" bigint DEFAULT 500000 NOT NULL;--> statement-breakpoint
ALTER TABLE "organizations" ADD COLUMN "last_auto_reload_at" timestamp with time zone;