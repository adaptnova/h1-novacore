import os
import json
from pathlib import Path

def search_extension_history(base_paths):
    print("Searching for VSCode extension history...")
    
    # Common extension history file patterns
    patterns = [
        "**/Code/User/globalStorage/*",
        "**/globalStorage/*",
        "**/*.json",
        "**/extensions/*",
        "**/state.vscdb*"
    ]
    
    found_files = []
    
    for base_path in base_paths:
        if not os.path.exists(base_path):
            print(f"\nPath not found: {base_path}")
            continue
            
        print(f"\nSearching in: {base_path}")
        
        for pattern in patterns:
            try:
                # Use Path.glob() to handle the wildcard pattern
                for file_path in Path(base_path).glob(pattern):
                    if file_path.is_file():
                        # Check if file might contain extension data
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(1024)  # Read first 1KB to check content
                                if any(keyword in content.lower() for keyword in ['extension', 'vscode', 'plugin', 'install']):
                                    found_files.append(file_path)
                                    print(f"\nPotential extension history found: {file_path}")
                                    print(f"File size: {os.path.getsize(file_path)} bytes")
                                    
                                    # Try to parse and display JSON content
                                    if file_path.suffix == '.json':
                                        try:
                                            with open(file_path, 'r', encoding='utf-8') as json_file:
                                                data = json.load(json_file)
                                                if isinstance(data, dict):
                                                    print("\nFile contents preview:")
                                                    for key in list(data.keys())[:5]:  # Show first 5 keys
                                                        print(f"  {key}")
                                        except json.JSONDecodeError:
                                            print("File is not valid JSON")
                        except (PermissionError, UnicodeDecodeError):
                            continue
            except Exception as e:
                print(f"Error searching pattern {pattern}: {str(e)}")
    
    return found_files

if __name__ == "__main__":
    # Paths to search
    search_paths = [
        "NovaMini",
        "/home/x/.config/Code",
        "/home/x/.vscode",
        "/home/x/.vscode-server",
        os.path.expanduser("~/.config/Code"),
        os.path.expanduser("~/.vscode"),
        os.path.expanduser("~/.vscode-server")
    ]
    
    print("Starting extension history search...")
    found_files = search_extension_history(search_paths)
    
    if not found_files:
        print("\nNo extension history files found.")
        print("You may need to check additional locations or ensure proper permissions.")
    else:
        print(f"\nFound {len(found_files)} potential extension history files.")