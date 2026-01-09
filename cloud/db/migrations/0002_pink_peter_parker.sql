CREATE TYPE "public"."outbox_status" AS ENUM('pending', 'processing', 'completed', 'failed');--> statement-breakpoint
CREATE TABLE "spans_outbox" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"span_id" uuid NOT NULL,
	"operation" text DEFAULT 'INSERT' NOT NULL,
	"status" "outbox_status" DEFAULT 'pending' NOT NULL,
	"retry_count" integer DEFAULT 0 NOT NULL,
	"last_error" text,
	"locked_at" timestamp,
	"locked_by" text,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"process_after" timestamp DEFAULT now() NOT NULL,
	"processed_at" timestamp,
	CONSTRAINT "spans_outbox_span_id_operation_unique" UNIQUE("span_id","operation")
);
--> statement-breakpoint
ALTER TABLE "spans_outbox" ADD CONSTRAINT "spans_outbox_span_id_spans_id_fk" FOREIGN KEY ("span_id") REFERENCES "public"."spans"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "spans_outbox_processable_idx" ON "spans_outbox" USING btree ("status","process_after","retry_count");--> statement-breakpoint
CREATE INDEX "spans_outbox_span_id_idx" ON "spans_outbox" USING btree ("span_id");