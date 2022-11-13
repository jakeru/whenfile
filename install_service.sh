#!/usr/bin/env sh

SCRIPT_DIR=$(dirname "$(realpath "$0")")

/usr/bin/systemctl --user enable "${SCRIPT_DIR}/whenfile.service"
/usr/bin/systemctl --user start whenfile
/usr/bin/systemctl --user status whenfile
