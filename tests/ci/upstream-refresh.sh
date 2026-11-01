#!/bin/sh
# Explicit release check independent of CI's digest. Never called at startup.
set -eu
cd "$(dirname "$0")/../.."
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT HUP INT TERM
printf '{"auths":{}}\n' > "$work/public-auth.json"
python3 tests/ci/export-trust.py
image=gcr.io/kaniko-project/executor:debug
podman pull --authfile "$work/public-auth.json" "$image"
podman image inspect "$image" --format '{{.Digest}}'
podman run --rm --network=none --cpus=1 --memory=512m --entrypoint /busybox/cat "$image" /kaniko/ssl/certs/ca-certificates.crt > "$work/upstream.pem"
sh tests/ci/kaniko-ca.sh "$work/upstream.pem" .ci-trust/ca-certificates.crt
