"""
Data Export Utilities for SMIF Dashboard
Handles exporting processed data to various formats for external analysis
"""
import pandas as pd
import json
import pickle
import zipfile
import io
import os
from datetime import datetime
import streamlit as st

class SMIFDataExporter:
    def __init__(self, results, metadata=None):
        self.results = results
        self.metadata = metadata or {}
        
    def to_excel_workbook(self):
        """Export all data to a comprehensive Excel workbook"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Main data sheets
            if 'returns' in self.results:
                self.results['returns'].to_excel(writer, sheet_name='Returns', index=True)
                
            if 'nav' in self.results:
                self.results['nav'].to_excel(writer, sheet_name='NAV', index=True)
                
            if 'positions' in self.results:
                self.results['positions'].to_excel(writer, sheet_name='Positions', index=True)
                
            if 'market_values' in self.results:
                self.results['market_values'].to_excel(writer, sheet_name='Market_Values', index=True)
                
            if 'weights' in self.results:
                self.results['weights'].to_excel(writer, sheet_name='Weights', index=True)
                
            if 'portfolio_summary' in self.results:
                self.results['portfolio_summary'].to_excel(writer, sheet_name='Portfolio_Summary', index=True)
                
            # Metadata sheet
            metadata_df = pd.DataFrame([self.metadata])
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # Tickers list
            if 'port_mkts' in self.results:
                tickers_df = pd.DataFrame({'Tickers': self.results['port_mkts']})
                tickers_df.to_excel(writer, sheet_name='Tickers', index=False)
        
        output.seek(0)
        return output
    
    def to_csv_package(self):
        """Export all data as a ZIP file containing CSV files"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Export each dataset as CSV
            datasets = ['returns', 'nav', 'positions', 'market_values', 'weights', 'portfolio_summary']
            
            for dataset in datasets:
                if dataset in self.results:
                    csv_buffer = io.StringIO()
                    self.results[dataset].to_csv(csv_buffer, index=True)
                    zip_file.writestr(f'{dataset}.csv', csv_buffer.getvalue())
            
            # Add metadata as JSON
            if self.metadata:
                zip_file.writestr('metadata.json', json.dumps(self.metadata, indent=2, default=str))
                
            # Add tickers list
            if 'port_mkts' in self.results:
                tickers_csv = '\n'.join(self.results['port_mkts'])
                zip_file.writestr('tickers.txt', tickers_csv)
        
        zip_buffer.seek(0)
        return zip_buffer
    
    def to_json_package(self):
        """Export data as JSON for programmatic access"""
        export_data = {}
        
        # Convert DataFrames to JSON-serializable format
        for key, value in self.results.items():
            if isinstance(value, pd.DataFrame):
                export_data[key] = {
                    'data': value.to_dict('records'),
                    'index': value.index.tolist() if hasattr(value.index, 'tolist') else list(value.index),
                    'columns': value.columns.tolist()
                }
            else:
                export_data[key] = value
        
        # Add metadata
        export_data['metadata'] = self.metadata
        
        return json.dumps(export_data, indent=2, default=str)
    
    def to_pickle_data(self):
        """Export raw Python objects as pickle for Jupyter/Python analysis"""
        export_package = {
            'results': self.results,
            'metadata': self.metadata,
            'export_timestamp': datetime.now().isoformat()
        }
        
        pickle_buffer = io.BytesIO()
        pickle.dump(export_package, pickle_buffer)
        pickle_buffer.seek(0)
        return pickle_buffer
    
    def get_colab_code(self):
        """Generate Python code for loading data in Google Colab"""
        code = f'''
# SMIF Portfolio Analysis - Google Colab Setup
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("📊 SMIF Portfolio Analysis Environment Ready!")
print("Last data update: {self.metadata.get('last_updated', 'Unknown')}")
print("Portfolio tickers: {', '.join(self.results.get('port_mkts', []))}")

# Data loading functions
def load_data_from_upload():
    """
    Upload the exported data files to Colab and load them
    """
    from google.colab import files
    
    print("📁 Please upload your data files...")
    uploaded = files.upload()
    
    data = {{}}
    
    # Handle different file types
    for filename, content in uploaded.items():
        if filename.endswith('.pkl'):
            import pickle
            data = pickle.loads(content)
            print(f"✅ Loaded pickle data: {{filename}}")
        elif filename.endswith('.zip'):
            import zipfile
            import io
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                for csv_file in zip_file.namelist():
                    if csv_file.endswith('.csv'):
                        df_name = csv_file.replace('.csv', '')
                        data[df_name] = pd.read_csv(zip_file.open(csv_file), index_col=0)
                        print(f"✅ Loaded CSV: {{csv_file}}")
    
    return data

# Quick analysis functions
def plot_performance_comparison(returns_df):
    """Plot SMIF vs benchmark performance"""
    if 'SMIF' in returns_df.columns and 'VTI' in returns_df.columns:
        nav = (1 + returns_df[['SMIF', 'VTI']]).cumprod()
        
        plt.figure(figsize=(12, 6))
        plt.plot(nav.index, nav['SMIF'], label='SMIF Portfolio', linewidth=2)
        plt.plot(nav.index, nav['VTI'], label='VTI Benchmark', linewidth=2)
        plt.title('Portfolio Performance vs Benchmark')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def analyze_portfolio_stats(returns_df):
    """Calculate and display portfolio statistics"""
    if 'SMIF' in returns_df.columns:
        stats = {{}}
        for col in ['SMIF', 'VTI']:
            if col in returns_df.columns:
                rtns = returns_df[col].dropna()
                stats[col] = {{
                    'Annual Return': (1 + rtns).prod() ** (252 / len(rtns)) - 1,
                    'Annual Volatility': rtns.std() * np.sqrt(252),
                    'Sharpe Ratio': rtns.mean() / rtns.std() * np.sqrt(252),
                    'Max Drawdown': ((1 + rtns).cumprod() / (1 + rtns).cumprod().cummax() - 1).min()
                }}
        
        stats_df = pd.DataFrame(stats).T
        stats_df = stats_df.round(4)
        
        print("📈 Portfolio Performance Statistics")
        print("=" * 50)
        display(stats_df)
        
        return stats_df

def plot_allocation_pie(weights_df):
    """Plot current portfolio allocation"""
    if not weights_df.empty:
        latest_weights = weights_df.iloc[-1]
        latest_weights = latest_weights[latest_weights > 0.01]  # Filter small positions
        
        plt.figure(figsize=(10, 8))
        plt.pie(latest_weights.values, labels=latest_weights.index, autopct='%1.1f%%', startangle=90)
        plt.title('Current Portfolio Allocation')
        plt.axis('equal')
        plt.show()

# Example usage:
print("\\n🚀 To get started:")
print("1. Run: data = load_data_from_upload()")
print("2. Then try:")
print("   - plot_performance_comparison(data['returns'])")
print("   - analyze_portfolio_stats(data['returns'])")
print("   - plot_allocation_pie(data['weights'])")
'''
        return code
    
    def get_jupyter_notebook(self):
        """Generate a complete Jupyter notebook for analysis"""
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# SMIF Portfolio Analysis\\n",
                        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n",
                        f"Last data update: {self.metadata.get('last_updated', 'Unknown')}\\n",
                        f"Portfolio holdings: {', '.join(self.results.get('port_mkts', []))}\\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Import required libraries\\n",
                        "import pandas as pd\\n",
                        "import numpy as np\\n",
                        "import matplotlib.pyplot as plt\\n",
                        "import seaborn as sns\\n",
                        "from datetime import datetime\\n",
                        "import warnings\\n",
                        "warnings.filterwarnings('ignore')\\n",
                        "\\n",
                        "# Set plotting style\\n",
                        "plt.style.use('seaborn-v0_8')\\n",
                        "sns.set_palette('husl')\\n",
                        "\\n",
                        "print('📊 Analysis environment ready!')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Load Data\\n",
                        "Upload your exported data files and load them into the notebook."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Load data from uploaded files\\n",
                        "# For Jupyter: Use file browser to upload\\n",
                        "# For Colab: Use files.upload()\\n",
                        "\\n",
                        "import pickle\\n",
                        "\\n",
                        "# Load pickle file (replace with your filename)\\n",
                        "with open('smif_data.pkl', 'rb') as f:\\n",
                        "    data_package = pickle.load(f)\\n",
                        "\\n",
                        "results = data_package['results']\\n",
                        "metadata = data_package['metadata']\\n",
                        "\\n",
                        "print(f'✅ Data loaded successfully!')\\n",
                        "print(f'Available datasets: {list(results.keys())}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Portfolio Performance Analysis"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Extract key datasets\\n",
                        "returns = results['returns']\\n",
                        "nav = results['nav']\\n",
                        "positions = results['positions']\\n",
                        "weights = results['weights']\\n",
                        "\\n",
                        "# Display basic info\\n",
                        "print(f'📅 Date range: {returns.index.min()} to {returns.index.max()}')\\n",
                        "print(f'📊 Portfolio holdings: {len(results[\"port_mkts\"])} positions')\\n",
                        "print(f'🎯 Holdings: {results[\"port_mkts\"]}')\\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Performance comparison chart\\n",
                        "plt.figure(figsize=(12, 6))\\n",
                        "plt.plot(nav.index, nav['SMIF'], label='SMIF Portfolio', linewidth=2)\\n",
                        "plt.plot(nav.index, nav['VTI'], label='VTI Benchmark', linewidth=2)\\n",
                        "plt.title('Portfolio Performance vs Benchmark')\\n",
                        "plt.xlabel('Date')\\n",
                        "plt.ylabel('Cumulative Return')\\n",
                        "plt.legend()\\n",
                        "plt.grid(True, alpha=0.3)\\n",
                        "plt.xticks(rotation=45)\\n",
                        "plt.tight_layout()\\n",
                        "plt.show()"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Portfolio Statistics"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Calculate performance statistics\\n",
                        "def calculate_stats(returns_series):\\n",
                        "    clean_returns = returns_series.dropna()\\n",
                        "    \\n",
                        "    annual_return = (1 + clean_returns).prod() ** (252 / len(clean_returns)) - 1\\n",
                        "    annual_vol = clean_returns.std() * np.sqrt(252)\\n",
                        "    sharpe = clean_returns.mean() / clean_returns.std() * np.sqrt(252)\\n",
                        "    \\n",
                        "    cumulative = (1 + clean_returns).cumprod()\\n",
                        "    drawdown = cumulative / cumulative.cummax() - 1\\n",
                        "    max_dd = drawdown.min()\\n",
                        "    \\n",
                        "    return {\\n",
                        "        'Annual Return': f'{annual_return:.2%}',\\n",
                        "        'Annual Volatility': f'{annual_vol:.2%}',\\n",
                        "        'Sharpe Ratio': f'{sharpe:.2f}',\\n",
                        "        'Max Drawdown': f'{max_dd:.2%}'\\n",
                        "    }\\n",
                        "\\n",
                        "# Compare SMIF vs VTI\\n",
                        "smif_stats = calculate_stats(returns['SMIF'])\\n",
                        "vti_stats = calculate_stats(returns['VTI'])\\n",
                        "\\n",
                        "comparison_df = pd.DataFrame({'SMIF': smif_stats, 'VTI': vti_stats})\\n",
                        "print('📈 Performance Comparison')\\n",
                        "print('=' * 40)\\n",
                        "display(comparison_df)"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Portfolio Allocation Analysis"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Current allocation pie chart\\n",
                        "latest_weights = weights.iloc[-1]\\n",
                        "latest_weights = latest_weights[latest_weights > 0.01]  # Filter small positions\\n",
                        "\\n",
                        "plt.figure(figsize=(10, 8))\\n",
                        "plt.pie(latest_weights.values, labels=latest_weights.index, autopct='%1.1f%%', startangle=90)\\n",
                        "plt.title('Current Portfolio Allocation')\\n",
                        "plt.axis('equal')\\n",
                        "plt.show()\\n",
                        "\\n",
                        "# Top holdings table\\n",
                        "top_holdings = latest_weights.sort_values(ascending=False).head(10)\\n",
                        "print('🏆 Top 10 Holdings')\\n",
                        "for ticker, weight in top_holdings.items():\\n",
                        "    print(f'{ticker}: {weight:.1%}')"
                    ]
                },
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Custom Analysis\\n",
                        "Add your own analysis code below:"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": [
                        "# Your custom analysis here\\n",
                        "# Examples:\\n",
                        "# - Sector analysis\\n",
                        "# - Risk attribution\\n",
                        "# - Factor exposure\\n",
                        "# - Rolling statistics\\n",
                        "\\n",
                        "print('✨ Ready for your custom analysis!')"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        return json.dumps(notebook, indent=2)