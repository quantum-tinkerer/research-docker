#!/bin/sh
# Retain after retiring the CA workaround: exercise executor's own Go TLS client.
# No registry login, image push, cache push, host ports or production resources.
set -eu
work=$(mktemp -d /kaniko/trust-probe.XXXXXX)
trap 'rm -rf "$work"; rm -f /research-native-tls-download' EXIT HUP INT TERM
probe() {
  host=$1
  printf 'FROM scratch\nADD https://%s/ /research-native-tls-download\n' "$host" > "$work/Dockerfile"
  /kaniko/executor --context="$work" --dockerfile="$work/Dockerfile" \
    --no-push --no-push-cache --cache=false > "$work/output" 2>&1
}
probe pypi.org || { cat "$work/output"; exit 1; }
for host in dv-g3b-emudhra.we-have-a-problem.com dv-g3b-aaa-emudhra.we-have-a-problem.com; do
  if probe "$host"; then echo "ERROR: incident chain trusted: $host" >&2; exit 1; fi
  grep -Eiq 'x509:.*(unknown authority|revoked|signature)' "$work/output" || { cat "$work/output"; exit 1; }
done
echo 'PASS: Kaniko native TLS/no-push build accepts PyPI and rejects both incident chains'
