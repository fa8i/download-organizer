#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(pwd)"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
VENV_NAME="${VENV_NAME:-venv}"
VENV_DIR="$PROJECT_DIR/$VENV_NAME"

APP_NAME="download-organizer"
DESKTOP_NAME="download-organizer.desktop"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/$DESKTOP_NAME"

LOG_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/download-organizer"
LOG_FILE="$LOG_DIR/app.log"

LAUNCHER_FILE="$PROJECT_DIR/run_download_organizer.sh"

echo "Project dir: $PROJECT_DIR"
echo "Python version requested: $PYTHON_VERSION"

# 1. Check and install system dependencies
echo "Checking system dependencies..."

REQUIRED_PKG=(
  "curl"
  "build-essential"
  "pkg-config"
  "libcairo2-dev"
  "libgirepository-2.0-dev"
  "gir1.2-gtk-4.0"
  "libgtk-4-dev"
  "wmctrl"
  "xdotool"
  "xwayland"
)

MISSING_PKG=()

for pkg in "${REQUIRED_PKG[@]}"; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        MISSING_PKG+=("$pkg")
    fi
done

if [ ${#MISSING_PKG[@]} -gt 0 ]; then
    echo "The following system dependencies are missing: ${MISSING_PKG[*]}"
    echo "They are required for PyGObject / GTK4 / Cairo / XWayland positioning."
    read -r -p "Would you like to install them now? (y/n): " confirm

    if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
        sudo apt update
        sudo apt install -y "${MISSING_PKG[@]}"
    else
        echo "Error: Missing dependencies. Install them manually and run install.sh again:"
        echo "sudo apt install ${MISSING_PKG[*]}"
        exit 1
    fi
fi

# 2. Ensure uv is available
if ! command -v uv >/dev/null 2>&1; then
    echo "uv not found. Installing uv..."

    export UV_INSTALL_DIR="${UV_INSTALL_DIR:-$HOME/.local/bin}"
    mkdir -p "$UV_INSTALL_DIR"

    curl -LsSf https://astral.sh/uv/install.sh | sh

    export PATH="$UV_INSTALL_DIR:$PATH"

    if [ -f "$HOME/.local/bin/env" ]; then
        # shellcheck disable=SC1090
        source "$HOME/.local/bin/env"
    fi
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "Error: uv installation finished but uv is not available in PATH."
    echo "Try opening a new terminal or add ~/.local/bin to PATH."
    exit 1
fi

echo "Using uv: $(command -v uv)"

# 3. Validate existing venv, recreate if broken or wrong Python version
RECREATE_VENV=false

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found."
    RECREATE_VENV=true
elif [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Virtual environment exists but has no Python executable."
    RECREATE_VENV=true
else
    CURRENT_VERSION="$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"

    if [ "$CURRENT_VERSION" != "$PYTHON_VERSION" ]; then
        echo "Existing venv uses Python ${CURRENT_VERSION:-unknown}, expected Python $PYTHON_VERSION."
        RECREATE_VENV=true
    fi
fi

if [ "$RECREATE_VENV" = true ]; then
    if [ -d "$VENV_DIR" ]; then
        BACKUP_DIR="$PROJECT_DIR/${VENV_NAME}.broken-$(date +%F-%H%M%S)"
        echo "Moving existing venv to: $BACKUP_DIR"
        mv "$VENV_DIR" "$BACKUP_DIR"
    fi

    echo "Installing Python $PYTHON_VERSION via uv if needed..."
    uv python install "$PYTHON_VERSION"

    echo "Creating virtual environment at $VENV_DIR..."
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION"
fi

PYTHON_EXEC="$VENV_DIR/bin/python"

echo "Python executable: $PYTHON_EXEC"
"$PYTHON_EXEC" --version

# 4. Install Python dependencies
if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "Error: requirements.txt not found."
    exit 1
fi

echo "Installing Python dependencies with uv..."
uv pip install --python "$PYTHON_EXEC" -r "$PROJECT_DIR/requirements.txt"

# Optional but useful for manual debugging
uv pip install --python "$PYTHON_EXEC" pip setuptools wheel

# 5. Define main script and user UID
if [ -z "${MAIN_SCRIPT:-}" ]; then
    MAIN_SCRIPT="$PROJECT_DIR/src/download_organizer/main.py"
fi

if [ -z "${USER_UID:-}" ]; then
    USER_UID="$(id -u)"
fi

echo "Detected configuration:"
echo "  Project Dir:  $PROJECT_DIR"
echo "  Python Exec:  $PYTHON_EXEC"
echo "  Main Script:  $MAIN_SCRIPT"
echo "  User UID:     $USER_UID"
echo "  Log File:     $LOG_FILE"

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Error: Main script not found: $MAIN_SCRIPT"
    exit 1
fi

# 6. Ensure .env exists if template is available
if [ -f "$PROJECT_DIR/.env.example" ] && [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "Created .env from .env.example. Remember to configure your LLM provider/API key."
fi

# 7. Disable legacy systemd user service
echo "Disabling legacy systemd user service if present..."

systemctl --user disable --now "$APP_NAME.service" >/dev/null 2>&1 || true

rm -f "$HOME/.config/systemd/user/$APP_NAME.service"
rm -rf "$HOME/.config/systemd/user/$APP_NAME.service.d"

systemctl --user daemon-reload >/dev/null 2>&1 || true

# 8. Create GNOME autostart launcher
echo "Creating launcher script..."

mkdir -p "$LOG_DIR"

cat > "$LAUNCHER_FILE" <<EOF
#!/bin/bash
set -euo pipefail

PROJECT_DIR="$PROJECT_DIR"
PYTHON_EXEC="$PYTHON_EXEC"
MAIN_SCRIPT="$MAIN_SCRIPT"
LOG_DIR="$LOG_DIR"
LOG_FILE="$LOG_FILE"

mkdir -p "\$LOG_DIR"

cd "\$PROJECT_DIR"

export PYTHONPATH="\$PROJECT_DIR/src"
export GDK_BACKEND="x11"
export PYTHONUNBUFFERED="1"

{
  echo "=================================================="
  echo "\$(date '+%Y-%m-%d %H:%M:%S') Starting Smart Download Organizer"
  echo "Project dir: \$PROJECT_DIR"
  echo "Python exec: \$PYTHON_EXEC"
  echo "Main script: \$MAIN_SCRIPT"
  echo "GDK_BACKEND=\$GDK_BACKEND"
  echo "PYTHONPATH=\$PYTHONPATH"
  echo "=================================================="
} >> "\$LOG_FILE"

exec "\$PYTHON_EXEC" "\$MAIN_SCRIPT" >> "\$LOG_FILE" 2>&1
EOF

chmod +x "$LAUNCHER_FILE"

echo "Creating GNOME autostart entry..."

mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Smart Download Organizer
Comment=Monitor Downloads folder and show interactive organizer dialog
Exec=$LAUNCHER_FILE
Path=$PROJECT_DIR
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Utility;
EOF

chmod +x "$AUTOSTART_FILE"

# 9. Start app now in the current graphical session
echo "Stopping existing running instances if any..."
pkill -f "$MAIN_SCRIPT" >/dev/null 2>&1 || true

echo "Starting Smart Download Organizer as a GNOME session app..."
nohup "$LAUNCHER_FILE" >/dev/null 2>&1 &

sleep 1

echo
echo "Installation completed successfully."
echo
echo "Runtime model:"
echo "  - GNOME autostart: $AUTOSTART_FILE"
echo "  - Launcher:        $LAUNCHER_FILE"
echo "  - Logs:            $LOG_FILE"
echo
echo "Useful commands:"
echo "  View logs:"
echo "    tail -f \"$LOG_FILE\""
echo
echo "  Stop app:"
echo "    pkill -f \"$MAIN_SCRIPT\""
echo
echo "  Start app manually:"
echo "    \"$LAUNCHER_FILE\""
echo
echo "  Test popup:"
DOWNLOAD_DIR="$(xdg-user-dir DOWNLOAD 2>/dev/null || true)"

if [ -z "$DOWNLOAD_DIR" ] || [ ! -d "$DOWNLOAD_DIR" ]; then
    if [ -d "$HOME/Downloads" ]; then
        DOWNLOAD_DIR="$HOME/Downloads"
    elif [ -d "$HOME/Descargas" ]; then
        DOWNLOAD_DIR="$HOME/Descargas"
    else
        DOWNLOAD_DIR="$HOME"
    fi
fi

echo "  Test popup:"
echo "    echo \"test\" > \"$DOWNLOAD_DIR/test_download_organizer.txt\""echo
echo "Note:"
echo "  This Ubuntu 26.04 / GNOME Wayland version intentionally uses GDK_BACKEND=x11"
echo "  because GTK4/Wayland does not allow reliable manual window positioning."