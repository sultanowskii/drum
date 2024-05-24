#!/bin/bash

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "usage: $0 src_file[.dr] input_file [output_format] [logfile]"
    exit 1
fi

SRC_FILE=$1
INPUT_FILE=$2

MAHCINE_ADDITIONAL_ARGS=""

# add output_format arg if specified
if [[ $# -ge 3 ]]; then
    MAHCINE_ADDITIONAL_ARGS="${MAHCINE_ADDITIONAL_ARGS} -O $3"
fi

# add logfile arg if specified
if [[ $# -ge 4 ]]; then
    MAHCINE_ADDITIONAL_ARGS="${MAHCINE_ADDITIONAL_ARGS} -L $4"
fi

COMPILED_FILE="${SRC_FILE}c"

# run compiler
./drumc.py "$SRC_FILE" "$COMPILED_FILE"

# run machine
./drumr.py "$COMPILED_FILE" "$INPUT_FILE" "$MAHCINE_ADDITIONAL_ARGS"
