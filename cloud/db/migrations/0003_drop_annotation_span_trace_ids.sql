ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_span_id_spans_id_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_trace_id_traces_id_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_span_otel_consistency_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_trace_otel_consistency_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_span_consistency_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_trace_consistency_fk";--> statement-breakpoint
ALTER TABLE "annotations" DROP CONSTRAINT IF EXISTS "annotations_span_id_environment_id_unique";--> statement-breakpoint
DROP INDEX IF EXISTS "annotations_trace_id_idx";--> statement-breakpoint
ALTER TABLE "annotations" DROP COLUMN IF EXISTS "span_id";--> statement-breakpoint
ALTER TABLE "annotations" DROP COLUMN IF EXISTS "trace_id";--> statement-breakpoint
CREATE INDEX "annotations_otel_trace_id_idx" ON "annotations" USING btree ("otel_trace_id");
