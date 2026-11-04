#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
"$project_dir/install.sh"
: "${PYTHON_BIN:=$project_dir/.venv/bin/python}"
export PYTHON_BIN

export MPLBACKEND=Agg
export MATPLOTLIBRC="$project_dir/matplotlibrc"
export MPLCONFIGDIR="$project_dir/cache/matplotlib"
export PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH=0

mkdir -p "$project_dir/cache"
rm -f "$project_dir/cache/errors.log"

if [ "${CORONADATA_RENDER_ONLY:-0}" != "1" ] && [ "${CORONADATA_DATA_READY:-0}" != "1" ]; then
    "$PYTHON_BIN" "$project_dir/scripts/runPipeline.py" update --report "$project_dir/cache/pipeline-report.json"
    export CORONADATA_DATA_READY=1

    # Render only for new data or changed render inputs, so the build time in
    # the output changes only when there is something new to publish.
    render_inputs=$(cd "$project_dir" && git ls-files -s scripts docs/templates data/measures-events.json \
        sources.json matplotlibrc requirements.txt creategraphs.sh | shasum | awk '{print $1}')
    render_marker="$project_dir/cache/last-render-inputs"
    data_changed=$("$PYTHON_BIN" -c 'import json, sys; print(json.load(open(sys.argv[1]))["changed"])' \
        "$project_dir/cache/pipeline-report.json")
    if [ "$data_changed" = "False" ] && [ "${CORONADATA_FORCE_RENDER:-0}" != "1" ] \
        && [ -f "$render_marker" ] && [ "$(cat "$render_marker")" = "$render_inputs" ]; then
        echo "No new data and no changed render inputs: skip rendering."
        exit 0
    fi
fi

# Workaround for strange download problem variants
# rm -f cache/COVID-19_varianten.json

cd "$project_dir/scripts"

# new combined graphs processing
"$PYTHON_BIN" ./createGraphs.py
"$PYTHON_BIN" ./createGraphs.py 365

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
"$PYTHON_BIN" ./buildSiteData.py
cd ..

if [ -n "${render_inputs:-}" ]; then
    echo "$render_inputs" > "$render_marker"
fi
