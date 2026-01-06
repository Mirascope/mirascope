-- Rollback initial ClickHouse analytics schema

DROP TABLE IF EXISTS {{database}}.annotations_analytics;
DROP TABLE IF EXISTS {{database}}.spans_analytics;
