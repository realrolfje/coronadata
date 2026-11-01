#!/bin/sh

set -eu

: "${PYTHON_BIN:=python3}"
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

export MPLBACKEND=Agg
export MATPLOTLIBRC="$project_dir/matplotlibrc"
export MPLCONFIGDIR="$project_dir/cache/matplotlib"
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=0

mkdir -p "$project_dir/cache"
rm -f "$project_dir/cache/errors.log"

if [ "${CORONADATA_RENDER_ONLY:-0}" != "1" ] && [ "${CORONADATA_DATA_READY:-0}" != "1" ]; then
    "$PYTHON_BIN" "$project_dir/scripts/runPipeline.py" update
    export CORONADATA_DATA_READY=1
fi

# Workaround for strange download problem variants
# rm -f cache/COVID-19_varianten.json

cd "$project_dir/scripts"

# new combined graphs processing
"$PYTHON_BIN" ./createGraphs.py
"$PYTHON_BIN" ./createGraphs.py 365

if [ "${CORONADATA_RENDER_ONLY:-0}" != "1" ]; then
    "$PYTHON_BIN" ./updatePageHits.py
else
    echo "Render-only mode: skip page-hit download."
fi
"$PYTHON_BIN" ./createPageHitsGraph.py

rm -f ../cache/stats.csv
lines=$(find . -name "*.py" | xargs cat | wc -l | awk '{print $1;}')
echo "python_lines;$lines" > ../cache/stats.csv
cachesize=$(du -sk ../cache | awk '{print $1;}')
echo "cache_size;$cachesize" >> ../cache/stats.csv

if [ "${CORONADATA_RENDER_ONLY:-0}" != "1" ]; then
    cd prikafspraak
    ./prikafspraak.sh
    cd ..
else
    echo "Render-only mode: skip vaccination appointment request."
fi

"$PYTHON_BIN" ./processTemplates.py
cd ..
