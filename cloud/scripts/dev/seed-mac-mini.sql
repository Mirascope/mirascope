-- Seed a Mac Mini row for local development.
-- Run against your local Postgres after applying migrations:
--   psql $DATABASE_URL -f cloud/scripts/dev/seed-mac-mini.sql

INSERT INTO mac_minis (hostname, agent_url, tunnel_hostname_suffix, max_claws)
VALUES ('dev-macbook', 'http://localhost:4111', 'claws.mirascope.dev', 6)
ON CONFLICT (hostname) DO UPDATE SET
  agent_url = EXCLUDED.agent_url,
  tunnel_hostname_suffix = EXCLUDED.tunnel_hostname_suffix,
  max_claws = EXCLUDED.max_claws;
