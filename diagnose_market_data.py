#!/usr/bin/env python3
"""Diagnose which stocks are causing the date range limitation"""

import pandas as pd
import yfinance as yf
from datetime import datetime

# Read the transaction file to get tickers
df_trans = pd.read_excel("data/Investment_Transaction_Detail_-_Customizable.xlsx")
portMkts = df_trans['Ticker/Option Symbol number'].tolist()
portMkts = sorted(set(portMkts), key=portMkts.index)
if 'NTPXX' in portMkts:
    portMkts.remove('NTPXX')

print(f"Analyzing {len(portMkts)} tickers: {portMkts}\n")

# Check each ticker's data availability
ticker_info = {}
problem_tickers = []

for ticker in portMkts:
    print(f"Checking {ticker}...", end=" ")
    try:
        data = yf.download(ticker, start='2023-09-01', end=None, progress=False, actions=True)
        if not data.empty:
            first_date = data.index[0]
            last_date = data.index[-1]
            num_days = len(data)
            
            ticker_info[ticker] = {
                'first_date': first_date,
                'last_date': last_date,
                'num_days': num_days,
                'status': 'OK'
            }
            
            # Check if this ticker might be limiting our data
            if last_date < pd.to_datetime('2024-01-01'):
                problem_tickers.append(ticker)
                ticker_info[ticker]['status'] = 'LIMITED'
                print(f"❌ Data only until {last_date.strftime('%Y-%m-%d')}")
            else:
                print(f"✓ Data through {last_date.strftime('%Y-%m-%d')}")
        else:
            ticker_info[ticker] = {'status': 'NO_DATA'}
            problem_tickers.append(ticker)
            print("❌ No data available")
    except Exception as e:
        ticker_info[ticker] = {'status': 'ERROR', 'error': str(e)}
        problem_tickers.append(ticker)
        print(f"❌ Error: {str(e)}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if problem_tickers:
    print(f"\n⚠️  Found {len(problem_tickers)} problematic tickers:")
    for ticker in problem_tickers:
        info = ticker_info[ticker]
        if info['status'] == 'LIMITED':
            print(f"  - {ticker}: Data only until {info['last_date'].strftime('%Y-%m-%d')}")
        elif info['status'] == 'NO_DATA':
            print(f"  - {ticker}: No data available")
        elif info['status'] == 'ERROR':
            print(f"  - {ticker}: Error - {info.get('error', 'Unknown')}")
    
    print("\n💡 Solution: The app should handle these tickers by:")
    print("   1. Using 'outer' join instead of default 'inner' join")
    print("   2. Or filtering out problematic tickers from the analysis")
    print("   3. Or filling missing data with last known values")
else:
    print("\n✅ All tickers have recent data available")

# Find the common date range
print("\n" + "="*60)
print("COMMON DATE RANGE ANALYSIS")
print("="*60)

valid_tickers = [t for t, info in ticker_info.items() if info['status'] == 'OK' or info['status'] == 'LIMITED']
if valid_tickers:
    # Get the latest "first date" and earliest "last date"
    latest_start = max(info['first_date'] for t, info in ticker_info.items() if 'first_date' in info)
    earliest_end = min(info['last_date'] for t, info in ticker_info.items() if 'last_date' in info)
    
    print(f"Latest start date across all tickers: {latest_start.strftime('%Y-%m-%d')}")
    print(f"Earliest end date across all tickers: {earliest_end.strftime('%Y-%m-%d')}")
    print(f"\nThis explains why data shows as: {latest_start.strftime('%Y-%m-%d')} to {earliest_end.strftime('%Y-%m-%d')}")