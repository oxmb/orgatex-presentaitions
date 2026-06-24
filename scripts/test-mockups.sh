#!/usr/bin/env bash
# Render every mockup HTML and assert a non-trivial PNG is produced.
set -euo pipefail
make mockups
shopt -s nullglob
html=(assets/mockups/*.html)
if [ ${#html[@]} -eq 0 ]; then echo "FAIL: no mockup HTML found" >&2; exit 1; fi
for f in "${html[@]}"; do
  png="${f%.html}.png"
  if [ ! -s "$png" ]; then echo "FAIL: missing/empty $png" >&2; exit 1; fi
  bytes="$(wc -c < "$png")"
  if [ "$bytes" -lt 5000 ]; then echo "FAIL: $png suspiciously small ($bytes B)" >&2; exit 1; fi
done
echo "OK: all mockups rendered"
