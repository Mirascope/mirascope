CREATE TYPE "public"."reservation_status" AS ENUM('active', 'released', 'expired');--> statement-breakpoint
CREATE TYPE "public"."request_status" AS ENUM('pending', 'success', 'failure');--> statement-breakpoint
CREATE TABLE "credit_reservations" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"stripe_customer_id" text NOT NULL,
	"estimated_cost_centicents" bigint NOT NULL,
	"status" "reservation_status" DEFAULT 'active' NOT NULL,
	"router_request_id" uuid NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"released_at" timestamp,
	"expires_at" timestamp NOT NULL
);
--> statement-breakpoint
CREATE TABLE "router_requests" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"provider" text NOT NULL,
	"model" text NOT NULL,
	"request_id" text,
	"input_tokens" bigint,
	"output_tokens" bigint,
	"cache_read_tokens" bigint,
	"cache_write_tokens" bigint,
	"cache_write_breakdown" jsonb,
	"cost_centicents" bigint,
	"status" "request_status" DEFAULT 'pending' NOT NULL,
	"error_message" text,
	"organization_id" uuid NOT NULL,
	"project_id" uuid NOT NULL,
	"environment_id" uuid NOT NULL,
	"api_key_id" uuid NOT NULL,
	"user_id" uuid NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"completed_at" timestamp
);
--> statement-breakpoint
ALTER TABLE "credit_reservations" ADD CONSTRAINT "credit_reservations_router_request_id_router_requests_id_fk" FOREIGN KEY ("router_request_id") REFERENCES "public"."router_requests"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "router_requests" ADD CONSTRAINT "router_requests_api_key_id_api_keys_id_fk" FOREIGN KEY ("api_key_id") REFERENCES "public"."api_keys"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "router_requests" ADD CONSTRAINT "router_requests_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE no action ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "credit_reservations_customer_status_index" ON "credit_reservations" USING btree ("stripe_customer_id","status");--> statement-breakpoint
CREATE INDEX "credit_reservations_expires_at_index" ON "credit_reservations" USING btree ("expires_at") WHERE "credit_reservations"."status" = 'active';--> statement-breakpoint
CREATE INDEX "router_requests_org_created_at_index" ON "router_requests" USING btree ("organization_id","created_at");--> statement-breakpoint
CREATE INDEX "router_requests_environment_index" ON "router_requests" USING btree ("environment_id");