#!/bin/sh

set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$project_dir"

supported_versions="3.12 3.13 3.14 3.15"

mkdir -p cache

python_version() {
    "$1" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null
}

is_supported() {
    case " $supported_versions " in
        *" $1 "*) return 0 ;;
        *) return 1 ;;
    esac
}

if [ -e .venv ] || [ -L .venv ]; then
    if is_supported "$(python_version .venv/bin/python || true)" \
        && cmp -s requirements.txt .venv/installed-requirements.txt \
        && .venv/bin/python -c "import matplotlib, numpy, scipy, pytz, certifi, tqdm" >/dev/null 2>&1; then
        exit 0
    fi
    echo "Removing .venv: it does not match requirements.txt or has no working Python $supported_versions."
    rm -rf .venv
fi

if [ -z "${PYTHON_SETUP_BIN:-}" ] && is_supported "$(python_version python3 || true)"; then
    PYTHON_SETUP_BIN=python3
fi
if [ -z "${PYTHON_SETUP_BIN:-}" ]; then
    for version in $supported_versions; do
        if command -v "python$version" >/dev/null 2>&1; then
            PYTHON_SETUP_BIN="python$version"
            break
        fi
    done
fi
if [ -z "${PYTHON_SETUP_BIN:-}" ]; then
    echo "No supported Python found. Install Python 3.12 or newer, for example with: brew install python@3.14" >&2
    exit 1
fi

echo "Creating virtual environment in .venv with $PYTHON_SETUP_BIN"
"$PYTHON_SETUP_BIN" -m venv .venv

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
cp requirements.txt .venv/installed-requirements.txt

echo "Dependencies installed in .venv."
