#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"

export CORONADATA_RENDER_ONLY=1
render_cache=${TMPDIR:-/tmp}/coronadata-render-cache
mkdir -p "$render_cache/matplotlib" "$render_cache/fontconfig"
export MPLCONFIGDIR="$render_cache/matplotlib"
export XDG_CACHE_HOME="$render_cache/fontconfig"
export MPLBACKEND=Agg
if [ -z "${PYTHON_BIN:-}" ] && [ -x "$project_dir/.venv/bin/python" ]; then
    PYTHON_BIN="$project_dir/.venv/bin/python"
fi
export PYTHON_BIN=${PYTHON_BIN:-python3}
exec ./creategraphs.sh
