import os
from pathlib import Path

def find_vscode_state_db():
    # Get the directory containing settings.json
    settings_path = "/home/x/.config/Code/User/settings.json"
    if os.path.exists(settings_path):
        print(f"Found settings.json at: {settings_path}")
        base_dir = os.path.dirname(settings_path)
        print(f"\nSearching in and around: {base_dir}")
        
        # Look in parent directories
        current = Path(base_dir)
        while current != current.parent:
            print(f"\nSearching in: {current}")
            # List all files in current directory
            try:
                for item in current.glob("**/*"):
                    if item.name == "state.vscdb":
                        print(f"\nFound database at: {item}")
                        print(f"File size: {os.path.getsize(item)} bytes")
                        print(f"Permissions: {oct(os.stat(item).st_mode)[-3:]}")
                        print(f"Readable: {os.access(item, os.R_OK)}")
                        return str(item)
            except PermissionError:
                print(f"Permission denied for some paths in {current}")
            current = current.parent
    
    # Additional VSCode paths to check
    additional_paths = [
        "/home/x/.config/Code/User/workspaceStorage",
        "/home/x/.config/Code/User/globalStorage",
        "/home/x/.vscode-server/data/User/globalStorage",
        "/home/x/.vscode-server/data/Machine",
    ]
    
    print("\nChecking additional VSCode paths...")
    for path in additional_paths:
        if os.path.exists(path):
            print(f"\nSearching in: {path}")
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file == "state.vscdb":
                            full_path = os.path.join(root, file)
                            print(f"\nFound database at: {full_path}")
                            print(f"File size: {os.path.getsize(full_path)} bytes")
                            print(f"Permissions: {oct(os.stat(full_path).st_mode)[-3:]}")
                            print(f"Readable: {os.access(full_path, os.R_OK)}")
                            return full_path
            except PermissionError:
                print(f"Permission denied for some paths in {path}")
        else:
            print(f"Path not found: {path}")
    
    return None

if __name__ == "__main__":
    print("Starting search for VSCode state database...")
    db_path = find_vscode_state_db()
    
    if not db_path:
        print("\nCould not find VSCode state database.")
        print("Please ensure VSCode is installed and has been run at least once.")
        
        # List contents of .config/Code directory if it exists
        code_dir = "/home/x/.config/Code"
        if os.path.exists(code_dir):
            print(f"\nContents of {code_dir}:")
            try:
                for item in os.listdir(code_dir):
                    print(f"  {item}")
            except PermissionError:
                print("Permission denied when trying to list directory contents")