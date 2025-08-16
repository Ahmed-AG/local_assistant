#!/usr/bin/env bash
# Run the MCP server from this repository.
# This script activates the local venv (if present), exports the
# service account key into an env var, and runs the server.

set -euo pipefail

# Ensure script runs from repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if it exists
if [ -f ".venv/bin/activate" ]; then
	# shellcheck disable=SC1091
	source .venv/bin/activate
fi

# Export GOOGLE_SERVICE_ACCOUNT_KEY when the key file exists
if [ -f "key-aviata-426903-42b52c15666d.json" ]; then
	export GOOGLE_SERVICE_ACCOUNT_KEY
	# Load the file content into the env var without printing it
	GOOGLE_SERVICE_ACCOUNT_KEY=$(cat key-aviata-426903-42b52c15666d.json)
	export GOOGLE_SERVICE_ACCOUNT_KEY
fi

exec python main.py
