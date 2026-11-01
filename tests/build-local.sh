#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
output=${1:-build-evidence/local-$(date -u +%Y%m%dT%H%M%SZ)}
mkdir -p "$output"
# Every rebuild gets its own receipt directory; never reuse a passing runtime log.
python3 - "$output" <<'PY'
import pathlib, sys
assert not any(pathlib.Path(sys.argv[1]).iterdir()), 'Choose an empty evidence directory'
PY
# Anonymous public-registry workflow: never load a user's registry credentials.
printf '{"auths":{}}\n' > "$output/public-auth.json"
available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
(( available >= 12 * 1024 * 1024 )) || { echo 'Need 12 GiB available memory'; exit 1; }
free_bytes=$(df --output=avail -B1 . | tail -1)
(( free_bytes >= 25 * 1024 * 1024 * 1024 )) || { echo 'Need 25 GiB disk'; exit 1; }
python3 -m unittest discover -s tests -p 'test_patch*.py' -v
python3 tests/source-contract.py
nice -n 15 ionice -c 3 timeout --signal=TERM --kill-after=30s 3600 \
  podman build --format=docker --authfile "$output/public-auth.json" \
  --jobs=1 --cpu-period=100000 --cpu-quota=400000 \
  --memory=8g --memory-swap=8g --layers \
  --iidfile "$output/image-id.txt" -t localhost/research-source:candidate image \
  > "$output/build.log" 2>&1
python3 tests/run-image.py "$(cat "$output/image-id.txt")" --output "$output/runtime"
