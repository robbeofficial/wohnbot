#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

# Avoid running multiple instances of the script
exec 200>/tmp/wohnbot.lock  # Open /tmp/wohnbot.lock and assign it to FD 200
flock -n 200 || { echo "Job is already running"; exit 1; }  # Try to lock FD 200

cd "${SCRIPT_DIR}"
source "${VENV_DIR}/bin/activate"
python -m wohnbot.main
