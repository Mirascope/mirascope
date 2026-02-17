-- Seed a local development Mac entry for your personal machine.
-- Run against your local Postgres database before using DEPLOYMENT_TARGET=mac-mini.
--
-- Customize hostname and agent_url for your machine. The hostname is just
-- a label — pick something that identifies your personal dev machine.
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
  'local-dev',                      -- change to your machine name if you prefer
  'http://localhost:8787',           -- point at your local agent (or Tailscale IP for a remote personal Mac)
  'local.claws.mirascope.dev',      -- local dev doesn't use tunnels, but the field is required
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
