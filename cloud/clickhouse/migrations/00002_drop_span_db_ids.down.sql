-- Restore legacy Postgres identifiers on spans_analytics

ALTER TABLE {{database}}.spans_analytics ADD COLUMN IF NOT EXISTS id UUID;
ALTER TABLE {{database}}.spans_analytics ADD COLUMN IF NOT EXISTS trace_db_id UUID;
