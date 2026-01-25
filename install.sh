#!/bin/bash

# Detect current directory
PROJECT_DIR=$(pwd)
# Detect virtual environment
VENV_DIR=""
for d in "venv" ".venv"; do
    if [ -d "$PROJECT_DIR/$d" ]; then
        VENV_DIR="$PROJECT_DIR/$d"
        break
    fi
done

if [ -z "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found."
    echo "Searched for: venv, .venv, env, .env"
    echo "Please create one first: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

PYTHON_EXEC="$VENV_DIR/bin/python"

echo "Detected configuration:"
echo "  Project Dir: $PROJECT_DIR"
echo "  Python Exec: $PYTHON_EXEC"
echo "  Main Script: $MAIN_SCRIPT"
echo "  User UID:    $USER_UID"

# Generate service file
SERVICE_FILE="download-organizer.service"
TEMPLATE_FILE="download-organizer.service.template"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file $TEMPLATE_FILE not found!"
    exit 1
fi

cp "$TEMPLATE_FILE" "$SERVICE_FILE"

# Replace placeholders
sed -i "s|{{PYTHON_EXEC}}|$PYTHON_EXEC|g" "$SERVICE_FILE"
sed -i "s|{{MAIN_SCRIPT}}|$MAIN_SCRIPT|g" "$SERVICE_FILE"
sed -i "s|{{WORKING_DIR}}|$PROJECT_DIR|g" "$SERVICE_FILE"
sed -i "s|{{USER_UID}}|$USER_UID|g" "$SERVICE_FILE"

echo "Generated $SERVICE_FILE with absolute paths."

# Install service
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

# Link service file to systemd user directory
ln -sf "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_FILE"
echo "Linked service to $SYSTEMD_DIR/$SERVICE_FILE"

# Reload systemd
systemctl --user daemon-reload
systemctl --user enable download-organizer
systemctl --user restart download-organizer

echo "Service installed and started successfully!"
echo "Check status with: systemctl --user status download-organizer"
