#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

export CORONADATA_RENDER_ONLY=1
render_cache=${TMPDIR:-/tmp}/coronadata-render-cache
mkdir -p "$render_cache/matplotlib" "$render_cache/fontconfig"
export MPLCONFIGDIR="$render_cache/matplotlib"
export XDG_CACHE_HOME="$render_cache/fontconfig"
export MPLBACKEND=Agg
exec ./creategraphs.sh
