#!/usr/bin/env bash
# Launch a pinned MCP server by id. Called from each plugin's .mcp.json.
# Resolves $HC_MCP_HOME (default ~/.healthcare-mcp) and execs the server on stdio.
# Exits non-zero with a readable reason if the server is not installed, so the
# client reports a failed server rather than hanging on a silent stdin.
set -euo pipefail
id="${1:?usage: mcp_launch.sh <server-id>}"
HOME_DIR="${HC_MCP_HOME:-$HOME/.healthcare-mcp}"
dir="$HOME_DIR/$id"

if [ ! -d "$dir" ]; then
  echo "healthcare-engines: MCP server '$id' is not installed at $dir." >&2
  echo "Run bin/install-mcp-servers.sh $id — until then this plugin's scripts still work." >&2
  exit 78   # EX_CONFIG
fi

if [ -x "$dir/.venv/bin/python" ]; then
  exec "$dir/.venv/bin/python" -m "$(echo "$id" | tr '-' '_')" "${@:2}"
elif [ -f "$dir/build/index.js" ]; then
  exec node "$dir/build/index.js" "${@:2}"
elif [ -f "$dir/dist/index.js" ]; then
  exec node "$dir/dist/index.js" "${@:2}"
else
  echo "healthcare-engines: '$id' is present but has no built entrypoint." >&2
  echo "Re-run bin/install-mcp-servers.sh $id and check the build output." >&2
  exit 78
fi
