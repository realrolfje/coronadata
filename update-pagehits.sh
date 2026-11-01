#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
: "${PYTHON_BIN:=python3}"

"$PYTHON_BIN" scripts/updatePageHits.py
CORONADATA_RENDER_ONLY=1 "$PYTHON_BIN" scripts/createPageHitsGraph.py

echo "Page-hit data updated separately from the epidemiological build."
