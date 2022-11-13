#!/usr/bin/env sh

SCRIPT_DIR=$(dirname "$(realpath "$0")")

WHENFILE_DIR="${SCRIPT_DIR}" /usr/bin/envsubst \
    < "${SCRIPT_DIR}/whenfile.service.tpl" \
    > "${SCRIPT_DIR}/whenfile.service"
