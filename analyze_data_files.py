#!/usr/bin/env python3
"""Analyze the Excel files to understand date ranges and data content"""

import pandas as pd
import numpy as np
from datetime import datetime

# Read the transaction file
print("=== Analyzing Investment Transaction File ===")
transaction_file = "data/Investment_Transaction_Detail_-_Customizable.xlsx"
df_trans = pd.read_excel(transaction_file)

print(f"Shape: {df_trans.shape}")
print(f"\nColumns: {list(df_trans.columns)}")

# Look for date columns
date_cols = [col for col in df_trans.columns if 'date' in col.lower() or 'd-' in col.lower()]
print(f"\nDate-related columns: {date_cols}")

# Analyze D-TRADE column (transaction dates)
if 'D-TRADE' in df_trans.columns:
    df_trans['D-TRADE'] = pd.to_datetime(df_trans['D-TRADE'])
    print(f"\nD-TRADE date range:")
    print(f"  Min: {df_trans['D-TRADE'].min()}")
    print(f"  Max: {df_trans['D-TRADE'].max()}")
    print(f"  Unique dates: {df_trans['D-TRADE'].nunique()}")
    
    # Show transactions by year
    df_trans['Year'] = df_trans['D-TRADE'].dt.year
    print(f"\nTransactions by year:")
    print(df_trans['Year'].value_counts().sort_index())

# Check tickers
if 'Ticker/Option Symbol number' in df_trans.columns:
    print(f"\nUnique tickers: {df_trans['Ticker/Option Symbol number'].nunique()}")
    print("Tickers:", sorted(df_trans['Ticker/Option Symbol number'].unique()))
    
    # Show last transaction date for each ticker
    print("\nLast transaction date by ticker:")
    last_dates = df_trans.groupby('Ticker/Option Symbol number')['D-TRADE'].max().sort_values(ascending=False)
    for ticker, date in last_dates.items():
        print(f"  {ticker}: {date.strftime('%Y-%m-%d')}")

print("\n" + "="*50 + "\n")

# Read the income file
print("=== Analyzing Income and Expense File ===")
income_file = "data/Income_and_Expense_Detail_Base_by_Account.xlsx"
df_income = pd.read_excel(income_file)

print(f"Shape: {df_income.shape}")
print(f"\nColumns: {list(df_income.columns)}")

# Look for date columns
date_cols = [col for col in df_income.columns if 'date' in col.lower()]
print(f"\nDate-related columns: {date_cols}")

# Analyze Recognition date
if 'Recognition date' in df_income.columns:
    # Filter out empty dates
    df_income_valid = df_income[df_income['Recognition date'].notna()]
    df_income_valid['Recognition date'] = pd.to_datetime(df_income_valid['Recognition date'], errors='coerce')
    df_income_valid = df_income_valid[df_income_valid['Recognition date'].notna()]
    
    print(f"\nRecognition date range (non-empty):")
    print(f"  Min: {df_income_valid['Recognition date'].min()}")
    print(f"  Max: {df_income_valid['Recognition date'].max()}")
    print(f"  Unique dates: {df_income_valid['Recognition date'].nunique()}")
    
    # Show income by year
    df_income_valid['Year'] = df_income_valid['Recognition date'].dt.year
    print(f"\nIncome entries by year:")
    print(df_income_valid['Year'].value_counts().sort_index())

# Sample of recent data
print("\n=== Sample of Recent Transaction Data ===")
if 'D-TRADE' in df_trans.columns:
    recent_trans = df_trans.nlargest(10, 'D-TRADE')[['D-TRADE', 'Ticker/Option Symbol number', 'Share/Par Value', 'A-PRIN-TRD-BSE']]
    print(recent_trans.to_string(index=False))

print("\n=== Analysis Summary ===")
print("The data analysis above shows the actual date ranges in your Excel files.")
print("If the data only goes to Sept 2023, that explains why the app shows that range.")