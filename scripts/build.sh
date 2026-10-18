#!/usr/bin/env bash
set -euo pipefail

: "${DESIGNER:?Set DESIGNER to the 1cv8 executable}"
: "${IB_CONNECTION:?Set IB_CONNECTION, for example /F/path/to/infobase}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_FILE="$ROOT_DIR/src/ПереносИсполнительныхЛистов.xml"
OUTPUT_DIR="$ROOT_DIR/build"
OUTPUT_FILE="$OUTPUT_DIR/ПереносИсполнительныхЛистов.epf"

mkdir -p "$OUTPUT_DIR"
"$DESIGNER" DESIGNER "$IB_CONNECTION" \
  /LoadExternalDataProcessorOrReportFromFiles "$SOURCE_FILE" "$OUTPUT_FILE" \
  /DisableStartupDialogs /DisableStartupMessages

test -s "$OUTPUT_FILE"
printf 'Built %s\n' "$OUTPUT_FILE"
