"""
Data persistence manager for SMIF Dashboard
Handles saving/loading processed data and metadata
"""
import json
import pickle
import os
from datetime import datetime
import pandas as pd
import streamlit as st

DATA_DIR = "data"
METADATA_FILE = os.path.join(DATA_DIR, "metadata.json")
RESULTS_FILE = os.path.join(DATA_DIR, "processed_results.pkl")

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_processed_data(results, upload_info):
    """Save processed results and metadata"""
    ensure_data_directory()
    
    # Save results
    with open(RESULTS_FILE, 'wb') as f:
        pickle.dump(results, f)
    
    # Save metadata
    metadata = {
        "last_updated": datetime.now().isoformat(),
        "uploaded_by": upload_info.get("email", "unknown"),
        "file_info": {
            "transaction_file": {
                "name": upload_info.get("transaction_name", "unknown"),
                "size": upload_info.get("transaction_size", 0)
            },
            "income_file": {
                "name": upload_info.get("income_name", "unknown"), 
                "size": upload_info.get("income_size", 0)
            }
        },
        "portfolio_summary": {
            "num_positions": len(results.get("port_mkts", [])),
            "tickers": results.get("port_mkts", []),
            "date_range": {
                "start": results.get("portfolio_summary", pd.DataFrame()).index.min().isoformat() if not results.get("portfolio_summary", pd.DataFrame()).empty else None,
                "end": results.get("portfolio_summary", pd.DataFrame()).index.max().isoformat() if not results.get("portfolio_summary", pd.DataFrame()).empty else None
            }
        }
    }
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

def load_processed_data():
    """Load saved processed results"""
    if not os.path.exists(RESULTS_FILE):
        return None
    
    try:
        with open(RESULTS_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading saved data: {str(e)}")
        return None

def get_metadata():
    """Get metadata about saved data"""
    if not os.path.exists(METADATA_FILE):
        return None
    
    try:
        with open(METADATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading metadata: {str(e)}")
        return None

def data_exists():
    """Check if processed data exists"""
    return os.path.exists(RESULTS_FILE) and os.path.exists(METADATA_FILE)

def delete_data():
    """Delete all saved data"""
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    if os.path.exists(METADATA_FILE):
        os.remove(METADATA_FILE)