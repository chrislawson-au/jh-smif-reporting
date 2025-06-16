# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the JH SMIF (Student-Managed Investment Fund) reporting system that analyzes investment portfolio performance and generates risk reports. The system processes brokerage transaction data and generates comprehensive performance analytics comparing the SMIF portfolio against benchmarks like VTI.

## Key Scripts

- `SMIFLivePerformance.py`: Main performance analysis script that processes transaction data and generates performance reports
- `SMIFLivePerformanceRiskReporting.py`: Extended version with additional risk decomposition analysis
- `historicalAlphaBeta.py`: Standalone utility for calculating alpha/beta statistics for specific ticker symbols

## Required Input Files

The scripts expect these Excel files to be present in the repository root:
- `Investment_Transaction_Detail_-_Customizable.xlsx`: Brokerage transaction report
- `Income_and_Expense_Detail_Base_by_Account.xlsx`: Income and expense report

## Running the System

### Web Dashboard (Recommended)
```bash
streamlit run streamlit_app.py
```

### Original Scripts (Legacy)
```bash
python SMIFLivePerformance.py
python SMIFLivePerformanceRiskReporting.py
python historicalAlphaBeta.py
```

## Dependencies

The scripts require:
- numpy
- pandas
- yfinance
- matplotlib
- statsmodels

## Generated Outputs

The scripts generate multiple CSV reports and PNG charts:
- Position tracking and market values
- Performance statistics vs benchmarks
- Risk decomposition analysis
- Visualization charts (SMIFvsVTI.png, drawdown comparisons)

## Web Dashboard Features

The Streamlit app (`streamlit_app.py`) provides:
- **Authentication**: Role-based access (admin upload, student view-only)
- **File Upload**: Web interface for Excel file processing
- **Interactive Charts**: Performance, allocation, drawdown analysis
- **Data Export**: CSV download capabilities
- **Real-time Processing**: Automatic report generation

### Authentication
- **Admin users**: admin1, admin2 (password: smif2024!) - can upload files
- **Students**: student (password: smifview) - view-only access

## Architecture Notes

- Market data is fetched from Yahoo Finance using yfinance
- Transaction data is processed to handle stock splits automatically
- Performance calculation uses a base initial value of $338,400
- Risk reporting focuses on active portfolio positions excluding VTI benchmark
- Weekly returns are used for alpha/beta regression analysis
- Web dashboard processes data in-memory without permanent file storage