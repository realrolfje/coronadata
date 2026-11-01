#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
: "${PYTHON_BIN:=.venv/bin/python}"

"$PYTHON_BIN" -m unittest discover -s tests
"$PYTHON_BIN" scripts/buildNormalizedData.py
"$PYTHON_BIN" scripts/checkNormalizedParity.py

echo "Development checks passed. Run CORONADATA_RENDER_ONLY=1 ./render.sh to rebuild charts offline."
