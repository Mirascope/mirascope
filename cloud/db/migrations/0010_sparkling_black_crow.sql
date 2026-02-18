CREATE TABLE "fleet_macs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"hostname" text NOT NULL,
	"model" text DEFAULT 'mini' NOT NULL,
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
	"status" text DEFAULT 'active' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now(),
	"updated_at" timestamp with time zone DEFAULT now(),
	CONSTRAINT "fleet_macs_hostname_unique" UNIQUE("hostname")
);
--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "mac_id" uuid;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "mac_port" integer;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "tunnel_hostname" text;--> statement-breakpoint
ALTER TABLE "claws" ADD COLUMN "mac_username" text;--> statement-breakpoint
ALTER TABLE "claws" ADD CONSTRAINT "claws_mac_id_fleet_macs_id_fk" FOREIGN KEY ("mac_id") REFERENCES "public"."fleet_macs"("id") ON DELETE no action ON UPDATE no action;