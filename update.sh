#!/bin/sh

set -eu

: "${PYTHON_BIN:=python3}"

if [ -n "$(git status --porcelain)" ]; then
    echo "Refusing to update: the working tree is not clean." >&2
    echo "Commit, stash, or discard local changes first." >&2
    exit 1
fi

git pull --ff-only
"$PYTHON_BIN" -m unittest discover -s tests
"$PYTHON_BIN" scripts/buildNormalizedData.py
"$PYTHON_BIN" scripts/checkNormalizedParity.py
PYTHON_BIN="$PYTHON_BIN" ./creategraphs.sh
"$PYTHON_BIN" scripts/checkBuildHealth.py

echo "Build completed without blocking source errors."
echo "Review the changes, then run ./publish.sh to commit and push generated data."
