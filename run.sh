#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"

# Avoid running multiple instances of the script
exec 200>/tmp/wohnbot.lock  # Open /tmp/wohnbot.lock and assign it to FD 200
flock -n 200 || { echo "$(date '+%Y-%m-%d %H:%M:%S') - Job is already running"; exit 1; }  # Try to lock FD 200

cd "${SCRIPT_DIR}"
source "${VENV_DIR}/bin/activate"
timeout 10m python -m wohnbot.main
EXIT_CODE=$?

# 4. Catch the timeout exit code (124) and log it
if [ $EXIT_CODE -eq 124 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Python script timed out after 10m and was killed."
fi
