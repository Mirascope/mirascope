ALTER TABLE "router_requests" ADD COLUMN "tool_usage" jsonb;--> statement-breakpoint
ALTER TABLE "router_requests" ADD COLUMN "tool_cost_centicents" bigint;