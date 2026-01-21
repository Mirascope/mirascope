-- Drop legacy Postgres identifiers from spans_analytics

ALTER TABLE {{database}}.spans_analytics DROP COLUMN IF EXISTS id;
ALTER TABLE {{database}}.spans_analytics DROP COLUMN IF EXISTS trace_db_id;
