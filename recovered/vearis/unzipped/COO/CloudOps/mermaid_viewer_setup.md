# Mermaid Diagram Viewer Setup

This document provides instructions for setting up tools to view Mermaid diagrams in our documentation.

## VSCode Extension Method

The simplest way to view Mermaid diagrams in VSCode is to install the Mermaid extension:

1. Open VSCode
2. Go to Extensions (Ctrl+Shift+X or Cmd+Shift+X)
3. Search for "Mermaid"
4. Install the "Markdown Preview Mermaid Support" extension by Matt Bierner
5. Open any markdown file with Mermaid diagrams
6. Use the "Open Preview" button (Ctrl+Shift+V or Cmd+Shift+V) to view the rendered diagrams

## Browser-Based Viewers

### Option 1: Mermaid Live Editor

1. Open a web browser
2. Go to https://mermaid.live/
3. Copy and paste the Mermaid diagram code into the editor
4. The diagram will render automatically on the right side

### Option 2: GitHub Gist

1. Create a GitHub Gist with your Markdown file containing Mermaid diagrams
2. GitHub will automatically render the Mermaid diagrams in the preview

## Command-Line Installation

If you prefer to install Mermaid tools via command line:

```bash
# Install Node.js and npm if not already installed
sudo apt update
sudo apt install nodejs npm

# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate PNG from Mermaid file
mmdc -i diagram.mmd -o diagram.png

# Generate SVG from Mermaid file
mmdc -i diagram.mmd -o diagram.svg
```

## Docker Method

You can also use Docker to render Mermaid diagrams:

```bash
# Pull the Mermaid CLI Docker image
docker pull minlag/mermaid-cli

# Generate PNG from Mermaid file
docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/diagram.mmd -o /data/diagram.png

# Generate SVG from Mermaid file
docker run --rm -v $(pwd):/data minlag/mermaid-cli -i /data/diagram.mmd -o /data/diagram.svg
```

## Extracting Mermaid Diagrams from Markdown

If you want to extract Mermaid diagrams from our Markdown files for rendering:

```bash
# Extract Mermaid diagrams from a Markdown file
grep -Pzo '```mermaid\n[\s\S]*?\n```' revised_architecture_diagram.md > extracted_diagrams.mmd

# Clean up the extracted file
sed -i 's/```mermaid//g' extracted_diagrams.mmd
sed -i 's/```//g' extracted_diagrams.mmd
```

## Recommended Setup for Our Environment

For our specific environment, I recommend:

1. Install the VSCode Mermaid extension for immediate viewing
2. Set up the Mermaid CLI for generating static images when needed
3. Consider setting up a simple web server to host HTML files with embedded Mermaid diagrams

## Example HTML File for Viewing

You can create a simple HTML file to view Mermaid diagrams:

```html
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
        }
        .diagram-container {
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        h1, h2 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Mermaid Diagram Viewer</h1>
    
    <h2>Overall Architecture</h2>
    <div class="diagram-container">
        <pre class="mermaid">
graph TD
    subgraph "IBM Cloud us-south Region"
        subgraph "us-south-2 Zone (Dallas 2)"
            subgraph "dataops-vpc"
                subgraph "dataops-subnet (10.240.64.0/24)"
                    DB1[nova-db-primary<br>MongoDB/PostgreSQL<br>bx2-8x32]
                    DB2[nova-db-graph<br>Neo4j/ArangoDB<br>bx2-8x32]
                    DB3[nova-db-timeseries<br>Redis/DragonflyDB<br>bx2-8x32]
                    GPU[ethos<br>GPU Server<br>gx3-48x240x2l40s]
                    LOG[nova-logs<br>Logging Server<br>bx2-4x16]
                end
                SG1[nova-db-sg<br>Security Group]
                SG2[ethos-sg<br>Security Group]
                SG3[nova-logs-sg<br>Security Group]
            end
            
            subgraph "us-south-default-vpc"
                subgraph "Default Subnet"
                    ADAPT[adapt<br>mx3d-96x960<br>Renamed from adapt3]
                end
                SG4[adapt-sg<br>Security Group]
            end
        end
        
        subgraph "Object Storage"
            OBJ[IBM Cloud Object Storage<br>Log Archives]
        end
    end
    
    SG1 --> DB1
    SG1 --> DB2
    SG1 --> DB3
    SG2 --> GPU
    SG3 --> LOG
    SG4 --> ADAPT
    
    DB1 -.-> |Log Forwarding| LOG
    DB2 -.-> |Log Forwarding| LOG
    DB3 -.-> |Log Forwarding| LOG
    GPU -.-> |Log Forwarding| LOG
    ADAPT -.-> |Log Forwarding| LOG
    
    LOG -.-> |Log Archiving| OBJ
        </pre>
    </div>

    <!-- Add more diagrams as needed -->
    
</body>
</html>
```

Save this as `mermaid_viewer.html` and open it in a web browser to view the diagrams.

## Conclusion

With these tools, you'll be able to view and work with the Mermaid diagrams in our documentation. The VSCode extension is the quickest way to get started, but the other methods provide additional flexibility for different use cases.