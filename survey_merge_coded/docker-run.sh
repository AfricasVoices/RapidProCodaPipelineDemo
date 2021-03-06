#!/bin/bash

set -e

IMAGE_NAME=demo-survey-merge-coded

# Check that the correct number of arguments were provided.
if [ $# -ne 7 ]; then
    echo "Usage: sh docker-run.sh <user> <json-input-path> <coding-mode> <coded-input-path> <key-of-raw> <json-output-path> <csv-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
CODING_MODE=$3
CODING_DIR=$4
KEY_OF_RAW=$5
OUTPUT_JSON=$6
OUTPUT_CSV=$7

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" --env CODING_MODE="$CODING_MODE" --env KEY_OF_RAW="$KEY_OF_RAW" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_JSON" "$container:/data/input.json"
docker cp "$CODING_DIR/." "$container:/data/coding"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_CSV")"
docker cp "$container:/data/output.csv" "$OUTPUT_CSV"
