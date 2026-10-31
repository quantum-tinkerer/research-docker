#!/bin/bash
set -euo pipefail
# Only a freshly source-built candidate; never export an existing runtime checkpoint.
image=$1
scanner=$(realpath "$2")
cd "$(dirname "$0")/.."
mkdir -p build-evidence
podman save --format docker-archive --output build-evidence/candidate.tar "$image"
sha256sum build-evidence/candidate.tar > build-evidence/candidate.tar.sha256
systemd-run --user --scope --quiet -p CPUQuota=400% -p MemoryMax=8G -p MemorySwapMax=0 \
  env GOMAXPROCS=4 GOMEMLIMIT=7GiB "$scanner" image \
  --input build-evidence/candidate.tar --cache-dir build-evidence/trivy-cache \
  --scanners vuln --ignore-unfixed --ignorefile /dev/null --list-all-pkgs \
  --format template --template '{{ toJson . }}' --output build-evidence/scan-results.json \
  --timeout 15m
