-- Seed a local development Mac Mini entry.
-- Run against your local Postgres database before using DEPLOYMENT_TARGET=mac-mini.
--
-- Usage:
--   psql $DATABASE_URL -f cloud/scripts/seed-dev-mini.sql

INSERT INTO mac_minis (
  hostname,
  agent_url,
  tunnel_hostname_suffix,
  max_claws,
  port_range_start,
  port_range_end,
  status
) VALUES (
  'dev-macbook',
  'http://localhost:8787',          -- point at your local agent or real Mac agent URL
  'claws.mirascope.dev',            -- tunnel suffix; claw hostname = claw-{id}.claws.mirascope.dev
  6,
  3001,
  3100,
  'active'
) ON CONFLICT (hostname) DO UPDATE SET
  agent_url = EXCLUDED.agent_url,
  tunnel_hostname_suffix = EXCLUDED.tunnel_hostname_suffix,
  max_claws = EXCLUDED.max_claws,
  port_range_start = EXCLUDED.port_range_start,
  port_range_end = EXCLUDED.port_range_end,
  status = EXCLUDED.status,
  updated_at = now();
