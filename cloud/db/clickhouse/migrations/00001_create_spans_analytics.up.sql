-- Create initial ClickHouse analytics schema
-- This file defines base tables and indexes for spans_analytics and annotations_analytics

-- =============================================================================
-- spans_analytics table
-- =============================================================================

CREATE TABLE IF NOT EXISTS {{database}}.spans_analytics (
    -- Core identifiers (id/trace_db_id for reference, not used for dedupe)
    id UUID,                  -- PostgreSQL span.id (reference)
    trace_db_id UUID,         -- PostgreSQL trace.id (reference)
    trace_id String,          -- OTEL trace_id (dedupe key)
    span_id String,           -- OTEL span_id (dedupe key)
    parent_span_id Nullable(String),

    -- Multi-tenant
    environment_id UUID,      -- dedupe key
    project_id UUID,
    organization_id UUID,

    -- Timing
    start_time DateTime64(9, 'UTC'),
    end_time Nullable(DateTime64(9, 'UTC')),  -- Nullable: spans may not have end_time yet
    duration_ms Nullable(Float64),  -- Nullable: null when end_time is missing

    -- Span metadata (name_lower for normalized search)
    name String,
    name_lower String MATERIALIZED lower(name),  -- for hasToken search
    kind Nullable(Int32),  -- Nullable: some spans may not have kind
    status_code Nullable(Int32),
    status_message Nullable(String),

    -- LLM-specific denormalized columns
    model Nullable(String),
    provider Nullable(String),
    input_tokens Nullable(Int64),
    output_tokens Nullable(Int64),
    total_tokens Nullable(Int64),
    cost_usd Nullable(Float64),
    function_id Nullable(UUID),
    function_name Nullable(String),
    function_version Nullable(String),
    error_type Nullable(String),
    error_message Nullable(String),

    -- Full attributes for ad-hoc queries (ZSTD compressed)
    attributes String CODEC(ZSTD(3)),
    events Nullable(String) CODEC(ZSTD(3)),
    links Nullable(String) CODEC(ZSTD(3)),

    -- Trace-level info (denormalized)
    service_name Nullable(String),
    service_version Nullable(String),
    resource_attributes Nullable(String) CODEC(ZSTD(3)),

    -- Sync metadata (version for ReplacingMergeTree)
    created_at DateTime64(3, 'UTC'),
    synced_at DateTime64(3, 'UTC') DEFAULT now64(3),
    _version UInt64 DEFAULT toUnixTimestamp64Milli(now64(3))
)
ENGINE = ReplacingMergeTree(_version)
PARTITION BY toYYYYMM(start_time)
ORDER BY (environment_id, start_time, trace_id, span_id, organization_id, project_id)
SETTINGS index_granularity = 8192;

-- Bloom filter indexes for spans_analytics
ALTER TABLE {{database}}.spans_analytics ADD INDEX IF NOT EXISTS idx_trace_id trace_id TYPE bloom_filter GRANULARITY 1;
ALTER TABLE {{database}}.spans_analytics ADD INDEX IF NOT EXISTS idx_span_id span_id TYPE bloom_filter GRANULARITY 1;
ALTER TABLE {{database}}.spans_analytics ADD INDEX IF NOT EXISTS idx_model model TYPE bloom_filter GRANULARITY 1;
ALTER TABLE {{database}}.spans_analytics ADD INDEX IF NOT EXISTS idx_function_id function_id TYPE bloom_filter GRANULARITY 1;
ALTER TABLE {{database}}.spans_analytics ADD INDEX IF NOT EXISTS idx_name_lower name_lower TYPE tokenbf_v1(10240, 3, 0) GRANULARITY 4;

-- =============================================================================
-- annotations_analytics table
-- =============================================================================

CREATE TABLE IF NOT EXISTS {{database}}.annotations_analytics (
    id UUID,
    span_db_id UUID,          -- PostgreSQL span.id
    trace_db_id UUID,         -- PostgreSQL trace.id
    otel_span_id String,      -- OTEL span_id (String for consistency)
    otel_trace_id String,     -- OTEL trace_id (String for consistency)
    label Nullable(Enum8('pass' = 1, 'fail' = 2)),
    reasoning Nullable(String) CODEC(ZSTD(3)),
    metadata Nullable(String) CODEC(ZSTD(3)),
    environment_id UUID,
    project_id UUID,
    organization_id UUID,
    created_by Nullable(UUID),
    created_at DateTime64(3, 'UTC'),
    updated_at DateTime64(3, 'UTC'),
    synced_at DateTime64(3, 'UTC') DEFAULT now64(3),
    _version UInt64 DEFAULT toUnixTimestamp64Milli(now64(3))
)
ENGINE = ReplacingMergeTree(_version)
PARTITION BY toYYYYMM(created_at)
ORDER BY (environment_id, otel_trace_id, otel_span_id, organization_id, project_id);

-- Bloom filter indexes for annotations_analytics
ALTER TABLE {{database}}.annotations_analytics ADD INDEX IF NOT EXISTS idx_otel_trace_id otel_trace_id TYPE bloom_filter GRANULARITY 1;
ALTER TABLE {{database}}.annotations_analytics ADD INDEX IF NOT EXISTS idx_environment_id environment_id TYPE bloom_filter GRANULARITY 1;
