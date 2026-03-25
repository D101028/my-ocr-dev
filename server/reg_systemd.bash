SCRIPT_PATH=$(dirname "$(readlink -f "$0")")
SERVICE_NAME="my-ocr-server"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PYTHON_SCRIPT="${SCRIPT_PATH}/app.py"

# Create systemd service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=My OCR Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_PATH
ExecStart=python3 $PYTHON_SCRIPT
Restart=on-failure
Environment="PATH=${SCRIPT_PATH}/.venv/bin:$PATH"
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon and enable service
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

echo "Service $SERVICE_NAME registered and started"
systemctl status "$SERVICE_NAME"
