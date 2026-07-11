#!/bin/bash
# run.sh — Wrapper to run the pipeline with correct library paths
# On macOS with Homebrew, WeasyPrint needs pango's dylib to be findable

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Set up library path for Homebrew dependencies (pango, etc.)
if [[ "$(uname)" == "Darwin" ]]; then
    BREW_PREFIX="$(brew --prefix 2>/dev/null || echo /opt/homebrew)"
    export DYLD_FALLBACK_LIBRARY_PATH="${BREW_PREFIX}/lib:${DYLD_FALLBACK_LIBRARY_PATH:-/usr/lib}"
fi

# Run the pipeline, forwarding all arguments
exec python3 "${SCRIPT_DIR}/src/pipeline.py" "$@"
