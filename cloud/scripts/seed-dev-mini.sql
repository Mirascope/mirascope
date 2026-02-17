-- Seed a local development Mac entry for your personal machine.
-- Run against your local Postgres database before using DEPLOYMENT_TARGET=mac-mini.
--
-- Prerequisites:
--   1. cloudflared installed and tunnel created on your personal Mac
--   2. Tunnel routes *.local-{user}.claws.mirascope.dev to your agent port
--   3. Agent running on your personal Mac
--
-- Customize the hostname, agent_url, and tunnel_hostname_suffix for your setup.
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
  'local-william',                                          -- your machine name
  'https://agent.local-william.claws.mirascope.dev',        -- agent exposed via tunnel (not localhost)
  'local-william.claws.mirascope.dev',                      -- claw tunnels: claw-{id}.local-william.claws.mirascope.dev
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
