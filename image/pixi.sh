# This hook is sourced by Jupyter so the policy also reaches notebook processes.
# Older Pixi releases can ignore native-root settings. Upgrade persistent-home
# binaries too: rebuilding the container alone does not replace them.
export PIXI_TLS_ROOT_CERTS=native
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_DIR=/etc/ssl/empty
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"
export CURL_CA_BUNDLE="$SSL_CERT_FILE"
export UV_NATIVE_TLS=true UV_SYSTEM_CERTS=true
export NODE_OPTIONS="${NODE_OPTIONS:+$NODE_OPTIONS }--use-openssl-ca"

PIXI_HOME="/home/$NB_USER/.pixi"
PIXI_BIN_DIR="$PIXI_HOME/bin"
PIXI_MIN_VERSION=0.82.1
PIXI_INSTALLED_VERSION=0
if [ -x "$PIXI_BIN_DIR/pixi" ]; then
    # Never execute a user-writable binary as root during the startup hook.
    PIXI_INSTALLED_VERSION=$(sudo -u "$NB_USER" -H "$PIXI_BIN_DIR/pixi" --version | awk '{print $2}')
fi
if [ "$(printf '%s\n' "$PIXI_MIN_VERSION" "$PIXI_INSTALLED_VERSION" | sort -V | head -n 1)" != "$PIXI_MIN_VERSION" ]; then
    case "$(uname -m)" in
        x86_64)
            PIXI_ARCHIVE=pixi-x86_64-unknown-linux-musl.tar.gz
            PIXI_SHA256=7ac72af79c50653bfcfddb2473b6e9eff2654affe0057d19fe21b0d8556a7fe2
            ;;
        aarch64)
            PIXI_ARCHIVE=pixi-aarch64-unknown-linux-musl.tar.gz
            PIXI_SHA256=6f4c4a101b84b15f33440f39fe5889afb1b77a4e88f02962248240cdcab56966
            ;;
        *) echo 'Unsupported Pixi architecture' >&2; return 1 ;;
    esac
    # Digests are from the official v0.82.1 GitHub release asset metadata.
    sudo -u "$NB_USER" -H env CURL_CA_BUNDLE="$SSL_CERT_FILE" \
        bash -s -- "$PIXI_HOME" "$PIXI_ARCHIVE" "$PIXI_SHA256" <<'INSTALL_PIXI' || return 1
set -euo pipefail
pixi_home=$1
archive=$2
digest=$3
mkdir -p "$pixi_home/bin"
tmp=$(mktemp -d "$pixi_home/.install-XXXXXX")
trap 'rm -rf "$tmp"' EXIT
curl --fail --silent --show-error --location \
    "https://github.com/prefix-dev/pixi/releases/download/v0.82.1/$archive" -o "$tmp/$archive"
printf '%s  %s\n' "$digest" "$tmp/$archive" | sha256sum --check --status
tar -xzf "$tmp/$archive" -C "$tmp" pixi
install -m 0755 "$tmp/pixi" "$pixi_home/bin/pixi"
INSTALL_PIXI
fi
export PIXI_HOME
case ":$PATH:" in
    *":$PIXI_BIN_DIR:"*) ;;
    *) export PATH="$PIXI_BIN_DIR:$PATH" ;;
esac
