#!/bin/bash

set -e

VENV_DIR=".venv"

# Dynamically resolve pyenv Python 3.12.8 path
PYTHON_PREFIX="$(pyenv prefix 3.12.8 2>/dev/null || true)"
PYTHON_BIN="$PYTHON_PREFIX/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Python 3.12.8 not found via pyenv."
    echo "Run 'pyenv install 3.12.8' and try again."
    exit 1
fi

echo "Using Python: $PYTHON_BIN"

# Create virtual environment
if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating Python virtual environment at '$VENV_DIR'..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# Activate venv
OS_TYPE=$(uname)
if [[ "$OS_TYPE" == "Darwin" || "$OS_TYPE" == "Linux" ]]; then
    source "$VENV_DIR/bin/activate"
else
    source "$VENV_DIR/Scripts/activate"
fi

# Install dependencies
echo "Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping package installation."
fi

echo "Setup complete. Virtual environment: $VENV_DIR"
