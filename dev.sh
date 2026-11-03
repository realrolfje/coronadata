#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

"$PYTHON_BIN" -m unittest discover -s tests
"$PYTHON_BIN" scripts/validateVariantTaxonomy.py
"$PYTHON_BIN" scripts/buildNormalizedData.py
"$PYTHON_BIN" scripts/checkNormalizedParity.py

echo "Development checks passed. Run CORONADATA_RENDER_ONLY=1 ./render.sh to rebuild charts offline."
