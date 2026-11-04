#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

"$PYTHON_BIN" scripts/updatePageHits.py
CORONADATA_RENDER_ONLY=1 "$PYTHON_BIN" scripts/createPageHitsGraph.py

echo "Page-hit data updated separately from the epidemiological build."
