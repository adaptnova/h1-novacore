#!/bin/bash

# Check if a file was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <markdown_file>"
    exit 1
fi

MARKDOWN_FILE=$1
TEMP_DIR="mermaid_temp"

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Extract Mermaid diagrams
echo "Extracting Mermaid diagrams from $MARKDOWN_FILE..."
grep -Pzo '```mermaid\n[\s\S]*?\n```' "$MARKDOWN_FILE" | sed 's/```mermaid//g' | sed 's/```//g' > "$TEMP_DIR/all_diagrams.mmd"

# Split into individual diagram files
csplit -z -f "$TEMP_DIR/diagram_" "$TEMP_DIR/all_diagrams.mmd" '/^graph/' '{*}' 2>/dev/null || csplit -z -f "$TEMP_DIR/diagram_" "$TEMP_DIR/all_diagrams.mmd" '/^gantt/' '{*}' 2>/dev/null || echo "No diagrams found or csplit failed"

echo "Diagrams extracted to $TEMP_DIR directory"
echo ""
echo "To generate PNG images, you need to install the Mermaid CLI:"
echo "npm install -g @mermaid-js/mermaid-cli"
echo ""
echo "After installation, you can generate PNG images with:"
echo "for diagram in \"$TEMP_DIR\"/diagram_*; do"
echo "    if [ -f \"\$diagram\" ]; then"
echo "        output_file=\"\${diagram%.*}.png\""
echo "        echo \"Processing \$diagram -> \$output_file\""
echo "        mmdc -i \"\$diagram\" -o \"\$output_file\" -b transparent"
echo "    fi"
echo "done"
echo ""
echo "Alternatively, you can use the online Mermaid Live Editor:"
echo "https://mermaid.live/"
echo ""
echo "Copy the contents of each diagram file and paste it into the editor to visualize and export as PNG."
