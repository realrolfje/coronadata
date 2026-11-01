#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"

if [ -z "${PYTHON_BIN:-}" ] && [ -x "$project_dir/.venv/bin/python" ]; then
    PYTHON_BIN="$project_dir/.venv/bin/python"
fi
PYTHON_BIN=${PYTHON_BIN:-python3}
PREVIEW_PORT=${PREVIEW_PORT:-8000}

if [ "${SKIP_RENDER:-0}" != "1" ]; then
    CORONADATA_RENDER_ONLY=1 PYTHON_BIN="$PYTHON_BIN" ./render.sh
fi

preview_url="http://127.0.0.1:$PREVIEW_PORT/"
echo "Serving the current working tree at $preview_url"
echo "Press Ctrl-C to stop."

if [ "${NO_OPEN:-0}" != "1" ] && command -v open >/dev/null 2>&1; then
    (sleep 1; open "$preview_url") &
fi

exec "$PYTHON_BIN" -m http.server "$PREVIEW_PORT" --bind 127.0.0.1 --directory docs
