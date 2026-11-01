#!/bin/sh
# Real-artifact regressions; run in the pinned Kaniko CI image before mutation.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
original=${1:?original released bundle required}
replacement=${2:?clean replacement required}
work=$(mktemp -d "${TMPDIR:-.}/kaniko-ca.XXXXXX")
trap 'rm -rf "$work"' EXIT HUP INT TERM
expect_error() {
  expected=$1; shift
  rc=0
  sh "$here/kaniko-ca.sh" "$@" > "$work/error" 2>&1 || rc=$?
  [ "$rc" = "$expected" ] || { cat "$work/error"; exit 1; }
}
cp "$original" "$work/supported.pem"
sh "$here/kaniko-ca.sh" "$work/supported.pem" "$replacement" --apply
cmp "$work/supported.pem" "$replacement"
expect_error 42 "$work/supported.pem" "$replacement" --apply
# Unknown affected bundle must never be overwritten.
cp "$original" "$work/drift.pem"
printf '\n# unreviewed upstream change\n' >> "$work/drift.pem"
cp "$work/drift.pem" "$work/before.pem"
expect_error 43 "$work/drift.pem" "$replacement" --apply
cmp "$work/drift.pem" "$work/before.pem"
printf 'not a PEM store\n' > "$work/invalid.pem"
expect_error 43 "$work/invalid.pem" "$replacement"
expect_error 43 "$original" "$original"
echo 'PASS: supported/apply, fixed/retire, drift/review, invalid PEM, unsafe replacement'
