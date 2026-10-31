set -euo pipefail
# Fresh disposable image home; no live user mount is supplied.
. /usr/local/bin/before-notebook.d/pixi.sh
pixi --version
[ "$PIXI_HOME" = "/home/$NB_USER/.pixi" ]
case ":$PATH:" in *":$PIXI_HOME/bin:"*) ;; *) exit 1;; esac
. /usr/local/bin/before-notebook.d/pixi.sh
pixi --version
cache="/home/$NB_USER/.cache"
[ "$(stat -c %u "/home/$NB_USER")" = "$NB_UID" ]
failed=0
for channel in conda-forge https://dv-g3b-emudhra.we-have-a-problem.com https://dv-g3b-aaa-emudhra.we-have-a-problem.com; do
 rc=0
 sudo -u "$NB_USER" -H env XDG_CACHE_HOME="$cache" SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt "$PIXI_HOME/bin/pixi" search --channel "$channel" zlib >/tmp/pixi-public-channel.log 2>&1 || rc=$?
 printf 'channel=%s rc=%s output_bytes=%s\n' "$channel" "$rc" "$(wc -c </tmp/pixi-public-channel.log)"
 if [ "$channel" = conda-forge ]; then
  if [ "$rc" != 0 ]; then failed=1; tail -30 /tmp/pixi-public-channel.log; fi
 elif [ "$rc" = 0 ] || ! grep -Eiq 'certificate|UnknownIssuer|invalid peer' /tmp/pixi-public-channel.log; then
  echo 'Certificate rejection not established';tail -30 /tmp/pixi-public-channel.log;failed=1
 else echo 'certificate rejected';fi
done
# Exercise persistent old/newer versions only inside this disposable test home.
real_pixi=$(mktemp "$PIXI_HOME/bin/.real-pixi-XXXXXX")
cp -p "$PIXI_HOME/bin/pixi" "$real_pixi"
trap 'mv "$real_pixi" "$PIXI_HOME/bin/pixi"' EXIT
printf '#!/bin/sh\n[ "$(id -u)" = 1000 ] || exit 88\necho "pixi 0.1.0"\n' > "$PIXI_HOME/bin/.probe-pixi"
chmod 755 "$PIXI_HOME/bin/.probe-pixi"
mv -f "$PIXI_HOME/bin/.probe-pixi" "$PIXI_HOME/bin/pixi"
. /usr/local/bin/before-notebook.d/pixi.sh
[ "$("$PIXI_HOME/bin/pixi" --version)" = 'pixi 0.82.1' ]
printf '#!/bin/sh\n[ "$(id -u)" = 1000 ] || exit 88\necho "pixi 999.0.0"\n' > "$PIXI_HOME/bin/.probe-pixi"
chmod 755 "$PIXI_HOME/bin/.probe-pixi"
mv -f "$PIXI_HOME/bin/.probe-pixi" "$PIXI_HOME/bin/pixi"
newer_sha=$(sha256sum "$PIXI_HOME/bin/pixi")
. /usr/local/bin/before-notebook.d/pixi.sh
[ "$(sha256sum "$PIXI_HOME/bin/pixi")" = "$newer_sha" ]
echo 'persistent old upgrade / current repeat / newer preservation passed'
exit "$failed"
