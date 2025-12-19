import sqlite3
import json
import os
from pathlib import Path

def check_file_access(path):
    return os.access(path, os.R_OK)

def explore_db(db_path):
    if not check_file_access(db_path):
        print(f"Error: No read permission for {db_path}")
        print(f"Current permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
        print("Please ensure you have the necessary permissions to access this file.")
        return

    try:
        print(f"Attempting to connect to: {db_path}")
        # Try to connect with URI flags to handle locked databases
        conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in database.")
            return
            
        print("\nDatabase Tables:")
        print("================")
        
        # Explore each table
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            
            try:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                print("\nColumns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"\nTotal rows: {count}")
                
                # Get sample data
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                    rows = cursor.fetchall()
                    
                    print("\nSample Data:")
                    for row in rows:
                        # Try to parse JSON if the data looks like JSON
                        formatted_row = []
                        for item in row:
                            if isinstance(item, str) and (item.startswith('{') or item.startswith('[')):
                                try:
                                    parsed = json.loads(item)
                                    formatted_row.append(json.dumps(parsed, indent=2))
                                except:
                                    formatted_row.append(item)
                            else:
                                formatted_row.append(item)
                        print(f"  {formatted_row}")
                
            except sqlite3.Error as e:
                print(f"Error accessing table {table_name}: {e}")
            
            print("\n" + "="*50)
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        print("\nCommon issues:")
        print("1. Database may be locked by VSCode")
        print("2. Insufficient permissions")
        print("3. Database file may be corrupted")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    db_path = "/home/x/.config/Code/User/globalStorage/state.vscdb"
    
    print("Checking database file...")
    if Path(db_path).exists():
        print(f"Database file found at: {db_path}")
        explore_db(db_path)
    else:
        print(f"Database file not found at: {db_path}")
        print("Please verify the path and ensure VSCode has created the database file.")