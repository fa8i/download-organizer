#!/bin/bash

PROJECT_DIR=$(dirname "$(readlink -f "$0")")

VENV_DIR=""
for d in "venv" ".venv"; do
    if [ -d "$PROJECT_DIR/$d" ]; then
        VENV_DIR="$PROJECT_DIR/$d"
        break
    fi
done

if [ -z "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found."
    exit 1
fi

PYTHON_EXEC="$VENV_DIR/bin/python"
export PYTHONPATH="$PROJECT_DIR/src"

echo "Launching Preferences..."
$PYTHON_EXEC -m download_organizer.ui.preferences
