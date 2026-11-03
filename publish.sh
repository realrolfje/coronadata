#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

"$PYTHON_BIN" scripts/checkBuildHealth.py
"$PYTHON_BIN" -m unittest discover -s tests
"$PYTHON_BIN" scripts/validateVariantTaxonomy.py
"$PYTHON_BIN" scripts/buildNormalizedData.py
"$PYTHON_BIN" scripts/checkNormalizedParity.py
"$PYTHON_BIN" scripts/checkPublishTree.py

git add --all -- data docs

if ! git diff --quiet; then
    echo "Refusing to publish: unstaged changes remain outside generated data." >&2
    echo "Only data/ and docs/ are staged automatically." >&2
    exit 1
fi

if git diff --cached --quiet; then
    echo "No meaningful generated changes to publish."
    exit 0
fi

message=${1:-Ran update script}
git commit -m "$message"
git push
