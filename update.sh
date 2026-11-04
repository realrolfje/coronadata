#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

if [ -n "$(git status --porcelain)" ]; then
    echo "Refusing to update: the working tree is not clean." >&2
    echo "Commit, stash, or discard local changes first." >&2
    exit 1
fi

git pull --ff-only
"$PYTHON_BIN" -m unittest discover -s tests
"$PYTHON_BIN" scripts/buildNormalizedData.py
"$PYTHON_BIN" scripts/checkNormalizedParity.py
./creategraphs.sh
"$PYTHON_BIN" scripts/validateVariantTaxonomy.py
"$PYTHON_BIN" scripts/checkBuildHealth.py

echo "Build completed without blocking source errors."
echo "Review the changes, then run ./publish.sh to commit and push generated data."
