#!/bin/bash
#
#   create_python_env.sh (C) 2024-2026, Peter Sulyok
#   This script will create a new virtual Python environment and will install all dependencies.
#

# Check if uv is installed, install it with pipx if not.
if ! command -v uv &> /dev/null;
then
    echo "uv is not installed, installing it with pipx..."
    pipx install uv
    if [[ "$?" -ne "0" ]];
    then
        echo "Error: pipx cannot install uv."
        exit 1
    fi
    pipx ensurepath
fi

# Use the specified Python version or determine the latest available one.
if [ "$1" = "" ];
then
    python_version=$(uv python list --all-versions 2>/dev/null | grep -oP 'cpython-\K[0-9]+\.[0-9]+\.[0-9]+' | sort -V | tail -1)
    if [ "$python_version" = "" ];
    then
        echo "Error: cannot determine the latest Python version."
        exit 1
    fi
    echo "Using latest available Python version: $python_version"
else
    python_version=$1
fi

# Install the specified Python version if it hasn't been already installed.
uv python install $python_version
if [[ "$?" -ne "0" ]];
then
    echo "Error: uv cannot install Python $python_version."
    exit 1
fi

# Create a virtual environment and install all dependencies (dev, lint, doc groups).
uv sync --python $python_version
if [[ "$?" -ne "0" ]];
then
    echo "Error: uv sync failed."
    exit 1
fi

# Notify user about required action.
echo ""
echo "Activate your new virtual Python environment!"
echo "-> source .venv/bin/activate"
exit 0
