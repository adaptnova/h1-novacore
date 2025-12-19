#!/bin/bash

# Script to install tools for viewing Mermaid diagrams

echo "Installing Mermaid viewer tools..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Installing Node.js and npm..."
    sudo apt update
    sudo apt install -y nodejs npm
else
    echo "Node.js is already installed."
fi

# Install Mermaid CLI
echo "Installing Mermaid CLI..."
npm install -g @mermaid-js/mermaid-cli

# Create HTML viewer
echo "Creating HTML viewer for Mermaid diagrams..."
cat > mermaid_viewer.html << 'EOL'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        });
    </script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .diagram-container {
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            overflow: auto;
        }
        h1, h2 {
            color: #333;
        }
        .controls {
            margin: 20px 0;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        button {
            padding: 8px 16px;
            margin-right: 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        textarea {
            width: 100%;
            height: 200px;
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
    </style>
</head>
<body>
    <h1>Mermaid Diagram Viewer</h1>
    
    <div class="controls">
        <h2>Load Diagram from File</h2>
        <input type="file" id="fileInput" accept=".md,.mmd,.txt">
        <button onclick="extractDiagrams()">Extract Diagrams</button>
        
        <h2>Custom Diagram</h2>
        <textarea id="customDiagram" placeholder="Paste your Mermaid diagram code here..."></textarea>
        <button onclick="renderCustomDiagram()">Render Diagram</button>
    </div>
    
    <div id="diagrams-container"></div>
    
    <script>
        // Function to extract Mermaid diagrams from Markdown
        function extractDiagrams() {
            const fileInput = document.getElementById('fileInput');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file first.');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                const diagramsContainer = document.getElementById('diagrams-container');
                diagramsContainer.innerHTML = '';
                
                // Extract Mermaid code blocks
                const regex = /```mermaid\n([\s\S]*?)\n```/g;
                let match;
                let diagramCount = 0;
                
                while ((match = regex.exec(content)) !== null) {
                    diagramCount++;
                    const diagramCode = match[1];
                    
                    const diagramDiv = document.createElement('div');
                    diagramDiv.className = 'diagram-container';
                    
                    const heading = document.createElement('h2');
                    heading.textContent = `Diagram ${diagramCount}`;
                    diagramDiv.appendChild(heading);
                    
                    const pre = document.createElement('pre');
                    pre.className = 'mermaid';
                    pre.textContent = diagramCode;
                    diagramDiv.appendChild(pre);
                    
                    diagramsContainer.appendChild(diagramDiv);
                }
                
                if (diagramCount === 0) {
                    diagramsContainer.innerHTML = '<p>No Mermaid diagrams found in the file.</p>';
                } else {
                    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
                }
            };
            
            reader.readAsText(file);
        }
        
        // Function to render custom diagram
        function renderCustomDiagram() {
            const customDiagram = document.getElementById('customDiagram').value;
            
            if (!customDiagram.trim()) {
                alert('Please enter a Mermaid diagram code.');
                return;
            }
            
            const diagramsContainer = document.getElementById('diagrams-container');
            diagramsContainer.innerHTML = '';
            
            const diagramDiv = document.createElement('div');
            diagramDiv.className = 'diagram-container';
            
            const heading = document.createElement('h2');
            heading.textContent = 'Custom Diagram';
            diagramDiv.appendChild(heading);
            
            const pre = document.createElement('pre');
            pre.className = 'mermaid';
            pre.textContent = customDiagram;
            diagramDiv.appendChild(pre);
            
            diagramsContainer.appendChild(diagramDiv);
            
            mermaid.init(undefined, document.querySelectorAll('.mermaid'));
        }
    </script>
</body>
</html>
EOL

# Create a script to extract diagrams from markdown files
echo "Creating script to extract diagrams from markdown files..."
cat > extract_mermaid_diagrams.sh << 'EOL'
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
EOL

# Make the extraction script executable
chmod +x extract_mermaid_diagrams.sh

echo "Creating a script to generate PNG images from Mermaid diagrams..."
cat > generate_diagram_images.sh << 'EOL'
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
csplit -z -f "$TEMP_DIR/diagram_" "$TEMP_DIR/all_diagrams.mmd" '/^graph/' '{*}' 2>/dev/null

# Generate PNG for each diagram
echo "Generating PNG images..."
for diagram in "$TEMP_DIR"/diagram_*; do
    if [ -f "$diagram" ]; then
        output_file="${diagram%.*}.png"
        echo "Processing $diagram -> $output_file"
        mmdc -i "$diagram" -o "$output_file" -b transparent
    fi
done

echo "Diagram images generated in $TEMP_DIR directory"
EOL

# Make the generation script executable
chmod +x generate_diagram_images.sh

# Print instructions
echo ""
echo "Installation complete!"
echo ""
echo "To view Mermaid diagrams, you can:"
echo "1. Open mermaid_viewer.html in a web browser"
echo "2. Use the file selector to load a markdown file with Mermaid diagrams"
echo "3. Click 'Extract Diagrams' to view the diagrams"
echo ""
echo "You can also extract diagrams from a markdown file using:"
echo "./extract_mermaid_diagrams.sh your_file.md"
echo ""
echo "To generate PNG images from diagrams in a markdown file:"
echo "./generate_diagram_images.sh your_file.md"
echo ""
echo "For VSCode, install the 'Markdown Preview Mermaid Support' extension"
echo "to view diagrams directly in the markdown preview."