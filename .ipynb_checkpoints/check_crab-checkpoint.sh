#!/bin/bash

CRAB_DIR="$1"
OUTPUT_FILE="$2"

status=$(crab status -d "$CRAB_DIR")

echo "$status"

if ! echo "$status" | grep -q "finished.*100.0%"; then
    echo "CRAB jobs are not fully finished."
    exit 1
fi

if ! echo "$status" | grep -q "Publication status.*done.*100.0%"; then
    echo "Publication is not finished."
    exit 1
fi

dataset=$(echo "$status" | awk '/Output dataset:/ {print $3}')

if [ -z "$dataset" ]; then
    echo "Could not find the output dataset."
    exit 1
fi

dasgoclient \
    -query="file dataset=$dataset instance=prod/phys03" |
    sed 's|^|root://cmseos.fnal.gov/|' \
    > "$OUTPUT_FILE"

echo "Created: $OUTPUT_FILE"
