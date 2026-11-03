#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "=== Sovereign Compute Taster ==="
echo "--- Demo ---"
python runner.py
echo ""
echo "--- Chaos ---"
bash chaos_tests/run_all_chaos.sh
echo ""
echo "=== Done ==="
echo "Full dual-ledger and production source available under license."
echo "Contact: jadesileywinditt@gmail.com"
