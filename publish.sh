#!/bin/sh

set -eu

: "${PYTHON_BIN:=python3}"

"$PYTHON_BIN" scripts/checkBuildHealth.py
"$PYTHON_BIN" -m unittest discover -s tests
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
