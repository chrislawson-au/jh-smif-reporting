# Option 3: Load from local file paths
# This is the recommended approach for organizational OneDrive files

if not data_loaded:
    # Specify your local file paths here
    # For OneDrive files, these are typically in your OneDrive folder
    # Example paths (update these with your actual paths):
    
    # Windows OneDrive path example:
    # transaction_path = r"C:\Users\YourName\OneDrive - Your Organization\path\to\Investment_Transaction_Detail_-_Customizable.xlsx"
    # income_path = r"C:\Users\YourName\OneDrive - Your Organization\path\to\Income_and_Expense_Detail_Base_by_Account.xlsx"
    
    # Mac OneDrive path example:
    # transaction_path = "/Users/YourName/OneDrive - Your Organization/path/to/Investment_Transaction_Detail_-_Customizable.xlsx"
    # income_path = "/Users/YourName/OneDrive - Your Organization/path/to/Income_and_Expense_Detail_Base_by_Account.xlsx"
    
    # UPDATE THESE PATHS WITH YOUR ACTUAL FILE LOCATIONS
    transaction_path = r"C:\Users\YourName\OneDrive\Investment_Transaction_Detail_-_Customizable.xlsx"
    income_path = r"C:\Users\YourName\OneDrive\Income_and_Expense_Detail_Base_by_Account.xlsx"
    
    print("Attempting to load files from local paths...")
    
    try:
        # Check if files exist
        import os
        
        if os.path.exists(transaction_path) and os.path.exists(income_path):
            transaction_data = pd.read_excel(transaction_path)
            income_data = pd.read_excel(income_path)
            data_loaded = True
            print("✓ Files loaded successfully from local paths!")
            print(f"  Transaction data: {len(transaction_data)} rows")
            print(f"  Income data: {len(income_data)} rows")
        else:
            print("❌ Files not found at specified paths.")
            if not os.path.exists(transaction_path):
                print(f"   Transaction file not found: {transaction_path}")
            if not os.path.exists(income_path):
                print(f"   Income file not found: {income_path}")
            print("\nTo find your OneDrive files:")
            print("1. Open File Explorer (Windows) or Finder (Mac)")
            print("2. Navigate to your OneDrive folder")
            print("3. Find your Excel files")
            print("4. Right-click and select 'Copy as path' (Windows) or 'Get Info' (Mac)")
            print("5. Update the paths in the cell above")
            data_loaded = False
            
    except Exception as e:
        print(f"❌ Error loading files: {str(e)}")
        print("\nMake sure:")
        print("- The file paths are correct")
        print("- You have the files synced locally if using OneDrive")
        print("- The files are not open in Excel")
        data_loaded = False