#!/usr/bin/env python3
"""
Database Tools Demo
Demonstrates the capabilities of the AA Database Tools
"""

import subprocess
import sys
import time

def run_command(cmd):
    """Run a command and return output"""
    print(f"\n{'>' * 60}")
    print(f"Running: {cmd}")
    print('>' * 60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")
    
    return result.returncode == 0

def demo_header(title):
    """Print demo section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def main():
    demo_header("AA Database Tools Demo")
    
    print("""
This demo showcases the AA Database Tools capabilities.

Prerequisites:
- At least one database should be running locally
- Or specify connection parameters in commands

The demo will:
1. Install dependencies
2. Test connection to databases
3. Check database status
4. Run sample queries
5. Demonstrate backup functionality
6. Show port scanning
""")
    
    input("\nPress Enter to continue...")
    
    # 1. Install dependencies
    demo_header("1. Installing Dependencies")
    run_command("cd aa-tools/database && ./aa-db-tools install")
    
    # 2. Test connections
    demo_header("2. Testing Database Connections")
    print("\nTesting Redis connection...")
    run_command("cd aa-tools/database && ./aa-db-tools test --type redis --json")
    
    print("\nTesting MongoDB connection...")
    run_command("cd aa-tools/database && ./aa-db-tools test --type mongodb --json")
    
    print("\nScanning for database ports on localhost...")
    run_command("cd aa-tools/database && ./aa-db-tools scan --host localhost")
    
    # 3. Check status
    demo_header("3. Checking Database Status")
    run_command("cd aa-tools/database && ./aa-db-tools status")
    
    # 4. Run queries
    demo_header("4. Running Sample Queries")
    print("\nNote: These queries require actual data in the databases")
    print("\nRunning Redis INFO command...")
    run_command("cd aa-tools/database && ./aa-db-tools query --type redis --query \"INFO\" --json")
    
    print("\nRunning Redis KEYS command...")
    run_command("cd aa-tools/database && ./aa-db-tools query --type redis --query \"KEYS *\" --json")
    
    # 5. Backup
    demo_header("5. Demonstrating Backup")
    print("\nNote: This will create backup files if databases are accessible")
    run_command("cd aa-tools/database && ./aa-db-tools backup --type redis --output ./demo_backups")
    
    # 6. Show help
    demo_header("6. Available Commands")
    run_command("cd aa-tools/database && ./aa-db-tools help")
    
    demo_header("Demo Complete")
    print("""
What you learned:

✓ How to install database dependencies
✓ How to test database connections
✓ How to check database status
✓ How to run queries on databases
✓ How to backup database data
✓ How to scan for database ports
✓ How to get help and usage information

Next Steps:
1. Configure databases with proper credentials
2. Run the tools with your specific connection parameters
3. Integrate these tools into your workflows
4. Check the README.md for advanced usage patterns

For more information:
- Read README.md for detailed documentation
- Check --help for each tool
- Look at the source code for customization
""")

if __name__ == "__main__":
    main()
