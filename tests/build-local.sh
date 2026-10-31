#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build-evidence
# Anonymous public-registry workflow: never load a user's registry credentials.
printf '{"auths":{}}\n' > build-evidence/public-auth.json
available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
(( available >= 12 * 1024 * 1024 )) || { echo 'Need 12 GiB available memory'; exit 1; }
free_bytes=$(df --output=avail -B1 . | tail -1)
(( free_bytes >= 25 * 1024 * 1024 * 1024 )) || { echo 'Need 25 GiB disk'; exit 1; }
python3 tests/source-contract.py
nice -n 15 ionice -c 3 timeout --signal=TERM --kill-after=30s 3600 \
  podman build --format=docker --authfile build-evidence/public-auth.json \
  --jobs=1 --cpu-period=100000 --cpu-quota=400000 \
  --memory=8g --memory-swap=8g --layers \
  --iidfile build-evidence/image-id.txt -t localhost/research-source:20261031 image \
  > build-evidence/build.log 2>&1
python3 tests/run-image.py "$(cat build-evidence/image-id.txt)" --output build-evidence/runtime
