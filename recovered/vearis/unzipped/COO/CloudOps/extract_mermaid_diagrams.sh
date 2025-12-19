#!/bin/bash

# Check if a file was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

MARKDOWN_FILE=$1
OUTPUT_FILE="${MARKDOWN_FILE%.*}_diagrams.mmd"

# Extract Mermaid diagrams
echo "Extracting Mermaid diagrams from $MARKDOWN_FILE to $OUTPUT_FILE..."
grep -Pzo '```mermaid\n[\s\S]*?\n```' "$MARKDOWN_FILE" > "$OUTPUT_FILE"

# Clean up the extracted file
sed -i 's/```mermaid//g' "$OUTPUT_FILE"
sed -i 's/```//g' "$OUTPUT_FILE"

echo "Extraction complete. Diagrams saved to $OUTPUT_FILE"
