#!/bin/bash

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "usage: $0 src_file[.dr] input_file"
    exit 1
fi

SRC_FILE=$1
INPUT_FILE=$2

COMPILED_FILE="${SRC_FILE}c"

./drumc.py $SRC_FILE $COMPILED_FILE

./drumr.py $COMPILED_FILE $INPUT_FILE
