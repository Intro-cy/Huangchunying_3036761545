#!/usr/bin/env bash
# Regenerate all tables and figures of the CK94 replication from the raw data.
# Usage: bash skills/scripts/regenerate.sh   (run from the repository root)
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 code/run_all.py
echo "All tables and figures regenerated in outputs/."
