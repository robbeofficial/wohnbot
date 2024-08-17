#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

cd "${SCRIPT_DIR}"
source "${VENV_DIR}/bin/activate"
python -m wohnbot.main
