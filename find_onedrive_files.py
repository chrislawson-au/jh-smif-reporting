"""
Helper script to find and load SMIF Excel files from OneDrive
Run this script to locate your files and get the correct paths
"""

import os
import pandas as pd
from pathlib import Path

def find_onedrive_folders():
    """Find OneDrive folders on the system"""
    possible_paths = []
    
    # Windows paths
    if os.name == 'nt':
        user_home = Path.home()
        # Check for various OneDrive folder patterns
        onedrive_patterns = [
            user_home / "OneDrive",
            user_home / "OneDrive - Johns Hopkins",
            user_home / "OneDrive - Johns Hopkins University",
            user_home / "OneDrive - JHU",
        ]
        
        # Also check in Documents
        doc_patterns = [
            user_home / "Documents" / "OneDrive",
            user_home / "Documents" / "OneDrive - Johns Hopkins",
        ]
        
        possible_paths.extend(onedrive_patterns)
        possible_paths.extend(doc_patterns)
        
        # Check environment variable
        onedrive_env = os.environ.get('OneDrive')
        if onedrive_env:
            possible_paths.append(Path(onedrive_env))
            
        # Check commercial OneDrive
        onedrive_commercial = os.environ.get('OneDriveCommercial')
        if onedrive_commercial:
            possible_paths.append(Path(onedrive_commercial))
    
    # Mac/Linux paths
    else:
        user_home = Path.home()
        possible_paths.extend([
            user_home / "OneDrive",
            user_home / "OneDrive - Johns Hopkins",
            user_home / "OneDrive - Johns Hopkins University",
        ])
    
    # Filter to existing paths
    existing_paths = [p for p in possible_paths if p.exists()]
    
    return existing_paths

def find_excel_files(directory, pattern):
    """Recursively find Excel files matching pattern"""
    matches = []
    try:
        for file in Path(directory).rglob("*.xlsx"):
            if pattern.lower() in file.name.lower():
                matches.append(file)
    except PermissionError:
        pass
    return matches

def main():
    print("=" * 60)
    print("SMIF FILE FINDER")
    print("=" * 60)
    
    # Find OneDrive folders
    print("\nSearching for OneDrive folders...")
    onedrive_folders = find_onedrive_folders()
    
    if not onedrive_folders:
        print("❌ No OneDrive folders found.")
        print("Please make sure OneDrive is installed and synced.")
        return
    
    print(f"\n✓ Found {len(onedrive_folders)} OneDrive folder(s):")
    for folder in onedrive_folders:
        print(f"  - {folder}")
    
    # Search for SMIF files
    print("\nSearching for SMIF Excel files...")
    
    transaction_files = []
    income_files = []
    
    for folder in onedrive_folders:
        # Search for transaction files
        trans_matches = find_excel_files(folder, "Investment_Transaction")
        transaction_files.extend(trans_matches)
        
        # Search for income files
        income_matches = find_excel_files(folder, "Income_and_Expense")
        income_files.extend(income_matches)
    
    # Display results
    if transaction_files:
        print(f"\n✓ Found {len(transaction_files)} transaction file(s):")
        for i, file in enumerate(transaction_files, 1):
            print(f"  {i}. {file}")
    else:
        print("\n❌ No transaction files found.")
    
    if income_files:
        print(f"\n✓ Found {len(income_files)} income file(s):")
        for i, file in enumerate(income_files, 1):
            print(f"  {i}. {file}")
    else:
        print("\n❌ No income files found.")
    
    # If files found, provide code to use
    if transaction_files and income_files:
        print("\n" + "=" * 60)
        print("COPY THIS CODE TO YOUR NOTEBOOK:")
        print("=" * 60)
        
        # Use the most recent files (by name, which usually includes date)
        trans_file = str(sorted(transaction_files)[-1])
        income_file = str(sorted(income_files)[-1])
        
        print(f"""
# Load SMIF data files from local OneDrive
transaction_path = r"{trans_file}"
income_path = r"{income_file}"

try:
    transaction_data = pd.read_excel(transaction_path)
    income_data = pd.read_excel(income_path)
    data_loaded = True
    print("✓ Files loaded successfully!")
    print(f"  Transaction data: {{len(transaction_data)}} rows")
    print(f"  Income data: {{len(income_data)}} rows")
except Exception as e:
    print(f"❌ Error loading files: {{str(e)}}")
    data_loaded = False
""")
        
        print("\n" + "=" * 60)
        
        # Try to load and preview the files
        print("\nAttempting to load and preview files...")
        try:
            trans_df = pd.read_excel(trans_file)
            income_df = pd.read_excel(income_file)
            
            print(f"\n✓ Transaction file loaded: {len(trans_df)} rows, {len(trans_df.columns)} columns")
            print(f"  Columns: {', '.join(trans_df.columns[:5])}...")
            
            print(f"\n✓ Income file loaded: {len(income_df)} rows, {len(income_df.columns)} columns")
            print(f"  Columns: {', '.join(income_df.columns[:5])}...")
            
        except Exception as e:
            print(f"\n⚠️ Could not preview files: {str(e)}")
    
    else:
        print("\n" + "=" * 60)
        print("MANUAL INSTRUCTIONS:")
        print("=" * 60)
        print("\n1. Open File Explorer (Windows) or Finder (Mac)")
        print("2. Navigate to your OneDrive folder")
        print("3. Find your SMIF Excel files:")
        print("   - Investment_Transaction_Detail_-_Customizable.xlsx")
        print("   - Income_and_Expense_Detail_Base_by_Account.xlsx")
        print("4. Right-click each file and select 'Copy as path'")
        print("5. Use the paths in your notebook")

if __name__ == "__main__":
    main()