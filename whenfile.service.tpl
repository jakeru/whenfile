[Unit]
Description=Whenfile

[Service]
Type=simple
ExecStart=${WHENFILE_DIR}/env/bin/python3 \
    ${WHENFILE_DIR}/whenfile.py \
    --runatstart \
    ${WHENFILE_DIR}/config.yaml

[Install]
WantedBy=default.target
