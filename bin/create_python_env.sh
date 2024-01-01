#!/bin/bash
#
#   create_python_env.sh (C) 2023, Peter Sulyok
#   This script will install python in a virtual environment with project dependencies.
#

# Check the first command-line parameter.
if [ "$1" = "" ];
then
    echo "Use: "$(basename "$0")" 3.12.1"
    exit -1
fi

# Install the specified python version if it hasn't been already installed.
python_version=$(pyenv version --bare|grep $1)
if [[ "$python_version" = "" || "$?" = "1" ]];
then
    pyenv install $1
fi
python_version=$1

# Select the python version locally.
pyenv local $python_version

# Create and activate a virtual environment.
python -m venv .venv-$python_version
. .venv-$python_version/bin/activate

# Upgrade pip and install required python modules.
pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -r docs/requirements-docs.txt

# Notify user about required activation.
echo ""
echo "Do not forget to activate the new Python virtual environment:"
echo "-> source .venv-$python_version/bin/activate"
