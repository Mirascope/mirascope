#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: db/clickhouse/migrate.sh <plan|migrate>

Commands:
  plan     Show the current migration version
  migrate  Apply all pending migrations
USAGE
}

command=${1:-}
if [[ -z "$command" ]]; then
  usage
  exit 1
fi

migrations_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/migrations"

clickhouse_url="${CLICKHOUSE_URL:-http://localhost:8123}"
clickhouse_user="${CLICKHOUSE_USER:-default}"
clickhouse_password="${CLICKHOUSE_PASSWORD:-clickhouse}"
clickhouse_database="${CLICKHOUSE_DATABASE:-mirascope_analytics}"
clickhouse_migrate_port="${CLICKHOUSE_MIGRATE_NATIVE_PORT:-}"
clickhouse_url_scheme="${clickhouse_url%%://*}"
clickhouse_tls_enabled="${CLICKHOUSE_TLS_ENABLED:-false}"

if [[ -n "${CLICKHOUSE_MIGRATE_DATABASE_URL:-}" ]]; then
  database_url="$CLICKHOUSE_MIGRATE_DATABASE_URL"
else
  clickhouse_url_no_proto="${clickhouse_url#*://}"
  clickhouse_url_no_proto="${clickhouse_url_no_proto%%/*}"

  host_port="$clickhouse_url_no_proto"
  if [[ "$host_port" == *":"* ]]; then
    host="${host_port%%:*}"
    port="${host_port##*:}"
  else
    host="$host_port"
    port=""
  fi

  migrate_port="$clickhouse_migrate_port"
  if [[ -z "$migrate_port" ]]; then
    if [[ "$clickhouse_tls_enabled" == "true" && -n "$port" && "$port" == "8443" ]]; then
      # ClickHouse Cloud: Use HTTPS port for native protocol with TLS
      migrate_port="$port"
    elif [[ "$clickhouse_url_scheme" == "http" || "$clickhouse_url_scheme" == "https" ]]; then
      migrate_port="9000"
    elif [[ -n "$port" ]]; then
      migrate_port="$port"
    else
      migrate_port="9000"
    fi
  fi

  # Build secure parameter for TLS connections
  secure_param=""
  if [[ "$clickhouse_tls_enabled" == "true" ]]; then
    secure_param="&secure=true"
  fi

  # URL-encode credentials to handle special characters (@, &, ?, :, etc.)
  encoded_user=$(printf %s "$clickhouse_user" | jq -sRr @uri)
  encoded_password=$(printf %s "$clickhouse_password" | jq -sRr @uri)
  # Use x-migrations-table-engine=MergeTree for ClickHouse Cloud compatibility
  # (Shared databases don't support TinyLog, the default engine)
  database_url="clickhouse://${host}:${migrate_port}/${clickhouse_database}?username=${encoded_user}&password=${encoded_password}${secure_param}&x-multi-statement=true&x-migrations-table-engine=MergeTree"
fi

# Global temp_dir for cleanup trap (must be global for EXIT trap to access)
temp_dir=""
trap 'if [[ -n "${temp_dir:-}" ]]; then rm -rf "$temp_dir"; fi' EXIT

prepare_migrations_directory() {
  local directory="$migrations_directory"

  if [[ -z "$clickhouse_database" ]]; then
    echo "$directory"
    return
  fi

  temp_dir="$(mktemp -d)"

  for file in "$directory"/*.sql; do
    if [[ -f "$file" ]]; then
      sed "s/{{database}}/${clickhouse_database}/g" "$file" > "$temp_dir/$(basename "$file")"
    fi
  done

  echo "$temp_dir"
}

run_migrate() {
  local action=$1
  shift
  local migrations_dir
  migrations_dir="$(prepare_migrations_directory)"

  if command -v migrate >/dev/null 2>&1; then
    TZ=UTC migrate -path "$migrations_dir" -database "$database_url" "$action" "$@"
    return
  fi

  local docker_database_url="$database_url"
  local docker_network_args=()

  if [[ "$(uname -s)" == "Linux" ]]; then
    docker_network_args=(--network host)
  else
    docker_database_url="${docker_database_url/localhost/host.docker.internal}"
    docker_database_url="${docker_database_url/127.0.0.1/host.docker.internal}"
  fi

  docker run --rm \
    -e TZ=UTC \
    -v "$migrations_dir:/migrations" \
    ${docker_network_args[@]:+"${docker_network_args[@]}"} \
    migrate/migrate \
    -path /migrations \
    -database "$docker_database_url" \
    "$action" "$@"
}

case "$command" in
  plan)
    if output=$(run_migrate version 2>&1); then
      echo "$output"
    elif echo "$output" | grep -qi "no migration"; then
      echo "$output"
    else
      echo "$output" >&2
      exit 1
    fi
    ;;
  migrate)
    echo "Running ClickHouse migrations..."
    echo "Database: $clickhouse_database"
    echo "Host: ${clickhouse_url#*://}"
    run_migrate up -verbose
    echo "Migrations complete."
    ;;
  *)
    usage
    exit 1
    ;;
esac
