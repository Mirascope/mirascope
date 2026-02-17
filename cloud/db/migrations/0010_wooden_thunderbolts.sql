CREATE TABLE "mac_minis" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"hostname" text NOT NULL,
	"tailscale_ip" text,
	"agent_url" text NOT NULL,
	"agent_auth_token_encrypted" text,
	"agent_auth_token_key_id" text,
	"chip" text,
	"ram_gb" integer,
	"disk_gb" integer,
	"max_claws" integer DEFAULT 12 NOT NULL,
	"port_range_start" integer DEFAULT 3001 NOT NULL,
	"port_range_end" integer DEFAULT 3100 NOT NULL,
	"tunnel_hostname_suffix" text NOT NULL,
	"status" text DEFAULT 'online' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "mac_minis_hostname_unique" UNIQUE("hostname")
);
--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "mini_id" uuid;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "mini_port" integer;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "tunnel_hostname" text;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_mini_id_mac_minis_id_fk" FOREIGN KEY ("mini_id") REFERENCES "public"."mac_minis"("id") ON DELETE no action ON UPDATE no action;