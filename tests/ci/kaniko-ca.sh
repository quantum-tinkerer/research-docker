#!/bin/sh
# Temporary workaround for https://github.com/GoogleContainerTools/kaniko
# (archived upstream): executor:debug still carries two incident roots.
# Reviewed artifact: sha256:9e22d0ba2c78cffbd47e2269aa6d3dc43fc3e3ecc6b61262399279dec5e67d45.
# Retire this script and .gitlab-ci.yml .ci-trust copying when a released
# executor has a clean CA store AND passes native TLS/build checks. Keep tests.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
original=${1:?usage: kaniko-ca.sh ORIGINAL REPLACEMENT [--apply]}
replacement=${2:?replacement required}
mode=${3:---check}
[ "$mode" = --check ] || [ "$mode" = --apply ] || exit 43
work=$(mktemp -d "${TMPDIR:-.}/kaniko-ca.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
review() { echo "ERROR: unsupported Kaniko CA source/API drift; code review required: $*" >&2; exit 43; }
scan() {
  input=$1
  rm -f "$work"/*.pem
  awk -v dir="$work" '
    /-----BEGIN CERTIFICATE-----/ { if (inside) exit 1; inside=1; n++ }
    inside { print > (dir "/" n ".pem") }
    /-----END CERTIFICATE-----/ { if (!inside) exit 1; inside=0 }
    END { if (inside || !n) exit 1 }
  ' "$input" || review 'invalid PEM boundaries'
  count=0
  for cert in "$work"/*.pem; do
    sed '/^-----/d' "$cert" | base64 -d > "$work/cert.der" || review 'invalid PEM encoding'
    fp=$(sha256sum "$work/cert.der" | awk '{print toupper($1)}')
    if grep -q "$fp" "$here/../blocked-fingerprints.json"; then count=$((count+1)); fi
  done
  echo "$count"
}
affected=$(scan "$original") || exit 43
if [ "$affected" = 0 ]; then
  echo 'ERROR: upstream CA fix detected; retire tests/ci/kaniko-ca.sh and .gitlab-ci.yml .ci-trust replacement, then rerun native TLS/build regression gates' >&2
  exit 42
fi
actual=$(sha256sum "$original" | awk '{print $1}')
[ "$actual" = 678d423fad6fb240a7d000f757d65fd96c757466ebd64e7031a78a64de26297a ] || review 'unreviewed affected bundle'
[ "$(scan "$replacement")" = 0 ] || review 'replacement contains blocked roots'
if [ "$mode" = --apply ]; then cp "$replacement" "$original"; fi
echo "PASS: reviewed affected Kaniko bundle ($affected incident roots); $mode"
