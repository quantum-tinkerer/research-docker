# Install Pixi in the persistent home directory as the notebook user. Later
# container starts preserve the installed version and any self-updates.
PIXI_HOME="/home/$NB_USER/.pixi"
PIXI_BIN_DIR="$PIXI_HOME/bin"
if [ ! -x "$PIXI_BIN_DIR/pixi" ]; then
    (
        set -o pipefail
        curl -fsSL https://pixi.sh/install.sh |
            sudo -u "$NB_USER" -H env \
                HOME="/home/$NB_USER" \
                PIXI_HOME="$PIXI_HOME" \
                PIXI_NO_PATH_UPDATE=1 \
                bash
    )
fi
export PIXI_HOME
case ":$PATH:" in
    *":$PIXI_BIN_DIR:"*) ;;
    *) export PATH="$PIXI_BIN_DIR:$PATH" ;;
esac
