#!/bin/bash
# generate-changelog.sh - Wrapper script for CHANGELOG generation
# Usage: ./generate-changelog.sh [--since-tag TAG] [--output FILE]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== CHANGELOG Generator ==="
echo ""

# Default values
SINCE_TAG=""
OUTPUT="CHANGELOG.md"
QUIET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --since-tag)
            SINCE_TAG="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT="$2"
            shift 2
            ;;
        --quiet)
            QUIET=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --since-tag TAG    Generate changelog since this tag"
            echo "  --output FILE      Output file (default: CHANGELOG.md)"
            echo "  --quiet            Only write file, don't print to stdout"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check prerequisites
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Error: Python 3 is required. Please install Python 3.8+."
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)

echo "Python: $PYTHON"
echo "Output: $OUTPUT"
if [[ -n "$SINCE_TAG" ]]; then
    echo "Since tag: $SINCE_TAG"
else
    echo "Since tag: (auto-detect)"
fi
echo ""

# Run the Python generator
ARGS=("$SCRIPT_DIR/generate_changelog.py" --output "$OUTPUT")
if [[ -n "$SINCE_TAG" ]]; then
    ARGS+=("--since-tag" "$SINCE_TAG")
fi
if [[ "$QUIET" == "true" ]]; then
    ARGS+=("--quiet")
fi

"$PYTHON" "${ARGS[@]}"

echo ""
echo "Done! Check $OUTPUT for the generated changelog."
