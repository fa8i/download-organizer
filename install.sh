#!/bin/bash

PROJECT_DIR=$(pwd)
# 1. Check and Install System Dependencies
echo "Checking system dependencies..."
REQUIRED_PKG=("libcairo2-dev" "pkg-config" "python3-dev" "libgirepository-2.0-dev" "gir1.2-gtk-3.0")
MISSING_PKG=()

for pkg in "${REQUIRED_PKG[@]}"; do
    if ! dpkg -l "$pkg" > /dev/null 2>&1; then
        MISSING_PKG+=("$pkg")
    fi
done

if [ ${#MISSING_PKG[@]} -gt 0 ]; then
    echo "The following system dependencies are missing: ${MISSING_PKG[*]}"
    echo "They are required for PyGObject and GUI functionality."
    read -p "Would you like to install them now? (y/n): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        sudo apt update
        sudo apt install -y "${MISSING_PKG[@]}"
    else
        echo "Error: Missing dependencies. Please install them manually and run install.sh again:"
        echo "sudo apt install ${MISSING_PKG[*]}"
        exit 1
    fi
fi

# 2. Detect virtual environment
VENV_DIR=""
for d in "venv" ".venv"; do
    if [ -d "$PROJECT_DIR/$d" ]; then
        VENV_DIR="$PROJECT_DIR/$d"
        break
    fi
done

if [ -z "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    VENV_DIR="$PROJECT_DIR/venv"
fi

echo "Updating Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

PYTHON_EXEC="$VENV_DIR/bin/python"

# Automatically define Main Script and User UID if not provided
if [ -z "$MAIN_SCRIPT" ]; then
    MAIN_SCRIPT="$PROJECT_DIR/src/download_organizer/main.py"
fi

if [ -z "$USER_UID" ]; then
    USER_UID=$(id -u)
fi

echo "Detected configuration:"
echo "  Project Dir: $PROJECT_DIR"
echo "  Python Exec: $PYTHON_EXEC"
echo "  Main Script: $MAIN_SCRIPT"
echo "  User UID:    $USER_UID"

SERVICE_FILE="download-organizer.service"
TEMPLATE_FILE="download-organizer.service.template"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file $TEMPLATE_FILE not found!"
    exit 1
fi

cp "$TEMPLATE_FILE" "$SERVICE_FILE"

sed -i "s|{{PYTHON_EXEC}}|$PYTHON_EXEC|g" "$SERVICE_FILE"
sed -i "s|{{MAIN_SCRIPT}}|$MAIN_SCRIPT|g" "$SERVICE_FILE"
sed -i "s|{{WORKING_DIR}}|$PROJECT_DIR|g" "$SERVICE_FILE"
sed -i "s|{{USER_UID}}|$USER_UID|g" "$SERVICE_FILE"

echo "Generated $SERVICE_FILE with absolute paths."

SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

ln -sf "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_FILE"
echo "Linked service to $SYSTEMD_DIR/$SERVICE_FILE"

systemctl --user daemon-reload
systemctl --user enable download-organizer
systemctl --user restart download-organizer

echo "Service installed and started successfully!"
echo "Check status with: systemctl --user status download-organizer"
