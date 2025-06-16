import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import statsmodels.api as sm
import io
import base64
from datetime import datetime
import hashlib
import data_manager
from data_exporter import SMIFDataExporter

# Configure page
st.set_page_config(
    page_title="SMIF Performance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import configuration from Streamlit secrets
try:
    # Try to load from Streamlit secrets first
    if hasattr(st, 'secrets') and 'emails' in st.secrets:
        ALLOWED_EMAILS = st.secrets['emails']['ALLOWED_EMAILS']
        CLASS_PASSWORD = st.secrets['passwords']['CLASS_PASSWORD']
        APP_TITLE = st.secrets['settings'].get('APP_TITLE', 'SMIF Performance Dashboard')
        INITIAL_PORTFOLIO_VALUE = st.secrets['settings'].get('INITIAL_PORTFOLIO_VALUE', 338400)
    else:
        # Fallback to config.py for legacy support (will be deprecated)
        from config import ALLOWED_EMAILS, CLASS_PASSWORD, APP_TITLE, INITIAL_PORTFOLIO_VALUE
        st.warning("⚠️ Using legacy config.py. Please migrate to Streamlit secrets for production deployment.")
except (ImportError, KeyError):
    # Demo configuration for testing
    st.error("⚠️ Configuration not found! Please set up .streamlit/secrets.toml or config.py")
    st.info("Demo mode: Use 'demo@university.edu' / 'demo123' to test")
    ALLOWED_EMAILS = ["demo@university.edu"]
    CLASS_PASSWORD = "demo123"
    APP_TITLE = "SMIF Dashboard (Demo Mode)"
    INITIAL_PORTFOLIO_VALUE = 338400

def check_password():
    """Returns True if user has correct email and password."""
    
    def credentials_entered():
        """Checks whether email and password entered by the user are correct."""
        email = st.session_state.get("email", "").strip().lower()
        password = st.session_state.get("password", "")
        
        if email in [e.lower() for e in ALLOWED_EMAILS] and password == CLASS_PASSWORD:
            st.session_state["password_correct"] = True
            st.session_state["user_email"] = email
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for email + password
        st.title("🔐 SMIF Dashboard Login")
        st.text_input("University Email", on_change=credentials_entered, key="email", placeholder="your.email@university.edu")
        st.text_input("Class Password", type="password", on_change=credentials_entered, key="password")
        st.info("📧 **Enter your university email address**\n\n🔑 **Use the class password provided by your instructor**")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.title("🔐 SMIF Dashboard Login")
        st.text_input("University Email", on_change=credentials_entered, key="email", placeholder="your.email@university.edu")
        st.text_input("Class Password", type="password", on_change=credentials_entered, key="password")
        st.error("😕 Invalid email or password. Contact your instructor if you need access.")
        return False
    else:
        # Password correct
        return True

def importYahooData(market, startdate='2023-09-01', enddate=None):
    """Import data from Yahoo Finance"""
    try:
        datax = yf.download(market, interval='1d', start=startdate, end=enddate, actions=True)
        
        if datax.empty:
            st.warning(f"No data available for {market}")
            return None, None, None, None
            
        datax.index = pd.DatetimeIndex(datax.index.strftime('%Y-%m-%d'))
        datax['Close.Rtns'] = datax['Close'].pct_change()
        
        # Handle missing Dividends column
        if 'Dividends' not in datax.columns:
            datax['Dividends'] = 0.0
        
        # Handle missing Stock Splits column  
        if 'Stock Splits' not in datax.columns:
            datax['Stock Splits'] = 0.0
            
        datax['Div.Rtns'] = datax['Dividends']/datax['Close'].shift(1)
        datax['Adj.Rtns'] = datax['Close.Rtns']+datax['Div.Rtns']
        datax['deltaClose'] = datax['Close'].diff(1)+datax['Dividends']
        
        return datax['Close'], datax['Adj.Rtns'], datax['Stock Splits'], datax['deltaClose']
        
    except Exception as e:
        st.error(f"Error downloading data for {market}: {str(e)}")
        return None, None, None, None

def calcPerfStats(rtns, scale=252):
    """Calculate performance statistics"""
    n = len(rtns.index)
    w = (1+rtns).prod()
    annRtn = w ** (scale/n) - 1
    annStd = rtns.std() * np.sqrt(scale)
    sRatio = annRtn / annStd
    nav = (1+rtns).cumprod()
    dd = nav/nav.cummax() - 1
    df = pd.DataFrame()
    for col in rtns.columns:
        df[col] = [annRtn[col], annStd[col], sRatio[col], dd.min()[col]]
    df.index = ['AnnRtn', 'AnnStd', 'Sharpe', 'MDD']
    return df, nav, dd

def process_smif_data(transaction_file, income_file):
    """Process SMIF data and generate reports"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Read Excel files
        status_text.text('Reading transaction data...')
        progress_bar.progress(0.1)
        smifReport = pd.read_excel(transaction_file)
        
        status_text.text('Reading income data...')
        progress_bar.progress(0.2)
        smifIncome = pd.read_excel(income_file)
        
        # Process income report
        status_text.text('Processing income data...')
        progress_bar.progress(0.3)
        def emptyStr(x): return(str(x).strip()!='')
        x = smifIncome['Recognition date'].to_list()
        smif_Income = smifIncome.loc[list(map(emptyStr,x)), ['Narrative - Short','Recognition date', 'Net amount - base']]
        smif_Income = smif_Income.set_index(smif_Income['Recognition date'])[['Narrative - Short','Net amount - base']]
        smif_Income.index = pd.to_datetime(smif_Income.index)
        smif_Income = smif_Income.groupby(['Recognition date']).apply('sum')['Net amount - base']
        
        # Get portfolio markets
        status_text.text('Extracting portfolio tickers...')
        progress_bar.progress(0.4)
        portMkts = smifReport['Ticker/Option Symbol number'].tolist()
        portMkts = sorted(set(portMkts), key=portMkts.index)
        if 'NTPXX' in portMkts:
            portMkts.remove('NTPXX')
        
        # Download market data
        status_text.text('Downloading market data from Yahoo Finance...')
        progress_bar.progress(0.5)
        dates = pd.date_range('2023-09-01', pd.to_datetime('today').strftime('%Y-%m-%d'), freq='B')
        df_close = pd.DataFrame(np.nan, columns=portMkts, index=dates)
        df_rtn = pd.DataFrame(np.nan, columns=portMkts, index=dates)
        df_splits = pd.DataFrame(np.nan, columns=portMkts, index=dates)
        
        for i, market in enumerate(portMkts):
            close_data, rtn_data, splits_data, _ = importYahooData(market, '2023-09-01')
            if close_data is not None:
                df_close[market] = close_data
                df_rtn[market] = rtn_data
                df_splits[market] = splits_data
            progress_bar.progress(0.5 + (i / len(portMkts)) * 0.3)
        
        df_rtn = df_rtn.loc[np.isnan(df_rtn.sum(axis=1, skipna=False)) == False, :]
        df_close = df_close.loc[df_rtn.index, :]
        df_splits.fillna(0, inplace=True)
        
        # Process transactions
        status_text.text('Processing transactions...')
        progress_bar.progress(0.8)
        reporting_dates = pd.DatetimeIndex(df_rtn['2023-09-14':].index)
        
        smifTrade = smifReport[['D-TRADE','Share/Par Value','A-PRIN-TRD-BSE','Ticker/Option Symbol number']]
        smifTrade = smifTrade.groupby(['D-TRADE','Ticker/Option Symbol number']).apply('sum')
        smifTrade = smifTrade.reset_index(level='Ticker/Option Symbol number')
        
        trades = pd.DataFrame(0.0, columns=portMkts, index=reporting_dates)
        
        for ticker in trades.columns:
            # Get trades for this ticker
            ticker_trades = smifTrade.loc[smifTrade['Ticker/Option Symbol number'] == ticker]
            
            if not ticker_trades.empty:
                # Align trade dates with our reporting dates
                for trade_date, trade_row in ticker_trades.iterrows():
                    trade_date_dt = pd.to_datetime(trade_date)
                    
                    # Find the nearest business day in our reporting dates
                    if trade_date_dt in reporting_dates:
                        trades.loc[trade_date_dt, ticker] = trade_row['Share/Par Value']
                    else:
                        # Find next available business day
                        next_dates = reporting_dates[reporting_dates >= trade_date_dt]
                        if len(next_dates) > 0:
                            trades.loc[next_dates[0], ticker] = trade_row['Share/Par Value']
                
                # Handle stock splits
                tradeDates = trades.loc[trades[ticker] != 0, ticker].index
                if len(tradeDates) > 0:
                    splitDates = df_splits.loc[df_splits[ticker] != 0, ticker].index
                    if len(splitDates) > 0:
                        for k in splitDates:
                            splitFactor = df_splits.loc[k, ticker]
                            tradesBeforeSplit = (trades.index < k)
                            trades.loc[tradesBeforeSplit, ticker] *= splitFactor
        
        positions = trades.cumsum()
        
        # Calculate market values and performance
        status_text.text('Calculating performance metrics...')
        progress_bar.progress(0.9)
        initV = INITIAL_PORTFOLIO_VALUE
        MktClose = df_close.loc[positions.index, :]
        MktValue = pd.DataFrame(positions[portMkts].values * MktClose[portMkts].values, 
                               columns=portMkts, index=positions.index)
        
        # Portfolio weights
        weights = MktValue.divide(MktValue.sum(axis=1), axis=0)
        
        # Trade costs
        smifTrade_filtered = smifTrade.loc[smifTrade['Ticker/Option Symbol number']!='NTPXX']
        tradeCosts = smifTrade_filtered.groupby(['D-TRADE']).apply('sum')['A-PRIN-TRD-BSE']
        
        # Portfolio components
        smifPort = pd.DataFrame(0.0, columns=['MktValue','Cost','Cash'], index=reporting_dates)
        smifPort['MktValue'] = MktValue.sum(axis=1)
        smifPort['Cost'] = tradeCosts
        smifPort['Cash'] = smif_Income
        smifPort.fillna(0, inplace=True)
        smifPort.loc['2023-09-14','Cash'] = initV
        
        # NAV and returns
        smifNav = smifPort['MktValue'] + smifPort['Cost'].cumsum() + smifPort['Cash'].cumsum()
        smifRtn = smifNav.pct_change()
        smifRtn.fillna(0, inplace=True)
        smifRtn = pd.DataFrame(smifRtn.values, columns=['SMIF'], index=pd.DatetimeIndex(smifRtn.index))
        
        # Combine with market returns
        res = smifRtn.join(df_rtn)
        res = res.iloc[1:, :]  # Start comparing returns from 09/15
        resNav = (1+res).cumprod()
        
        progress_bar.progress(1.0)
        status_text.text('Analysis complete!')
        
        return {
            'returns': res,
            'nav': resNav,
            'positions': positions,
            'market_values': MktValue,
            'weights': weights,
            'portfolio_summary': smifPort,
            'trade_costs': tradeCosts,
            'port_mkts': portMkts
        }
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return None

def main():
    if not check_password():
        return
    
    # Sidebar
    st.sidebar.title("📈 SMIF Dashboard")
    if 'user_email' in st.session_state:
        st.sidebar.write(f"Welcome, **{st.session_state['user_email']}**!")
    else:
        st.sidebar.write("Please log in to access the dashboard.")
    
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Main content
    st.title(f"📊 {APP_TITLE}")
    st.markdown("---")
    
    # Load existing data if available
    if 'results' not in st.session_state and data_manager.data_exists():
        st.session_state['results'] = data_manager.load_processed_data()
    
    # Data overview section
    metadata = data_manager.get_metadata()
    if metadata:
        st.header("📊 Current Data Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            st.metric(
                "Last Updated", 
                last_updated.strftime("%Y-%m-%d"),
                delta=last_updated.strftime("%H:%M")
            )
        
        with col2:
            st.metric(
                "Portfolio Positions", 
                metadata['portfolio_summary']['num_positions']
            )
        
        with col3:
            st.metric(
                "Uploaded By",
                metadata['uploaded_by'].split('@')[0] if '@' in metadata['uploaded_by'] else metadata['uploaded_by']
            )
        
        # File details in expander
        with st.expander("📋 Data Details"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transaction File")
                st.write(f"**Name:** {metadata['file_info']['transaction_file']['name']}")
                st.write(f"**Size:** {metadata['file_info']['transaction_file']['size']:,} bytes")
            
            with col2:
                st.subheader("Income File")
                st.write(f"**Name:** {metadata['file_info']['income_file']['name']}")
                st.write(f"**Size:** {metadata['file_info']['income_file']['size']:,} bytes")
            
            st.subheader("Portfolio Holdings")
            tickers = metadata['portfolio_summary']['tickers']
            if tickers:
                # Display tickers in a nice grid
                ticker_cols = st.columns(min(6, len(tickers)))
                for i, ticker in enumerate(tickers):
                    with ticker_cols[i % len(ticker_cols)]:
                        st.code(ticker)
            
            date_range = metadata['portfolio_summary']['date_range']
            if date_range['start'] and date_range['end']:
                st.subheader("Data Range")
                start_date = datetime.fromisoformat(date_range['start']).strftime("%Y-%m-%d")
                end_date = datetime.fromisoformat(date_range['end']).strftime("%Y-%m-%d")
                st.write(f"**From:** {start_date} **To:** {end_date}")
        
        # Add option to clear data
        if st.button("🗑️ Clear Saved Data", help="Remove all saved data and start fresh"):
            data_manager.delete_data()
            if 'results' in st.session_state:
                del st.session_state['results']
            st.success("Data cleared successfully!")
            st.rerun()
        
        st.markdown("---")
    
    # File upload section
    if 'user_email' in st.session_state:
        st.header("📁 Upload Files")
        
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_file = st.file_uploader(
                "Investment Transaction Detail", 
                type=['xlsx'],
                help="Upload the Investment_Transaction_Detail_-_Customizable.xlsx file"
            )
        
        with col2:
            income_file = st.file_uploader(
                "Income and Expense Detail", 
                type=['xlsx'],
                help="Upload the Income_and_Expense_Detail_Base_by_Account.xlsx file"
            )
        
        if transaction_file and income_file:
            if st.button("🚀 Generate Reports", type="primary"):
                with st.spinner('Processing data...'):
                    upload_info = {
                        "email": st.session_state.get('user_email', 'unknown'),
                        "transaction_name": transaction_file.name,
                        "transaction_size": transaction_file.size,
                        "income_name": income_file.name,
                        "income_size": income_file.size
                    }
                    
                    results = process_smif_data(transaction_file, income_file)
                    
                    if results:
                        # Save data for persistence
                        data_manager.save_processed_data(results, upload_info)
                        st.session_state['results'] = results
                        st.success("✅ Reports generated and saved successfully!")
                        st.balloons()
    
    # Display results section
    if 'results' in st.session_state:
        st.markdown("---")
        st.header("📈 Performance Analysis")
        
        results = st.session_state['results']
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        if 'SMIF' in results['returns'].columns and 'VTI' in results['returns'].columns:
            perf_stats, _, dd = calcPerfStats(results['returns'][['SMIF', 'VTI']])
            
            with col1:
                st.metric(
                    "SMIF Annual Return", 
                    f"{perf_stats.loc['AnnRtn', 'SMIF']:.2%}",
                    delta=f"{perf_stats.loc['AnnRtn', 'SMIF'] - perf_stats.loc['AnnRtn', 'VTI']:.2%}"
                )
            
            with col2:
                st.metric(
                    "SMIF Volatility", 
                    f"{perf_stats.loc['AnnStd', 'SMIF']:.2%}"
                )
            
            with col3:
                st.metric(
                    "SMIF Sharpe Ratio", 
                    f"{perf_stats.loc['Sharpe', 'SMIF']:.2f}",
                    delta=f"{perf_stats.loc['Sharpe', 'SMIF'] - perf_stats.loc['Sharpe', 'VTI']:.2f}"
                )
            
            with col4:
                st.metric(
                    "Max Drawdown", 
                    f"{perf_stats.loc['MDD', 'SMIF']:.2%}"
                )
        
        # Charts
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "🥧 Allocation", "📉 Drawdown", "📋 Data"])
        
        with tab1:
            st.subheader("Cumulative Performance vs VTI")
            if 'SMIF' in results['nav'].columns and 'VTI' in results['nav'].columns:
                chart_data = results['nav'][['SMIF', 'VTI']].copy()
                st.line_chart(chart_data, height=400)
            
            # Regression analysis
            if 'SMIF' in results['returns'].columns and 'VTI' in results['returns'].columns:
                st.subheader("SMIF vs VTI Regression")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                x_data = results['returns']['VTI']
                y_data = results['returns']['SMIF']
                
                ax.scatter(x_data, y_data, alpha=0.6)
                
                # Fit regression line
                X = sm.add_constant(x_data)
                model = sm.OLS(y_data, X).fit()
                ax.plot(x_data, model.fittedvalues, 'r-', linewidth=2, label=f'Alpha: {model.params[0]:.4f}')
                
                ax.set_xlabel('VTI Returns')
                ax.set_ylabel('SMIF Returns')
                ax.set_title('SMIF vs VTI Scatter Plot')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
                # Display regression stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Alpha", f"{model.params[0]:.4f}")
                with col2:
                    st.metric("Beta", f"{model.params[1]:.4f}")
                with col3:
                    st.metric("R-squared", f"{model.rsquared:.3f}")
        
        with tab2:
            st.subheader("Current Portfolio Allocation")
            if not results['weights'].empty:
                latest_weights = results['weights'].iloc[-1]
                latest_weights = latest_weights[latest_weights > 0].sort_values(ascending=False)
                
                # Pie chart
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.pie(latest_weights.values, labels=latest_weights.index, autopct='%1.1f%%', startangle=90)
                ax.set_title('Current Portfolio Allocation')
                st.pyplot(fig)
                
                # Table
                st.subheader("Allocation Details")
                allocation_df = pd.DataFrame({
                    'Ticker': latest_weights.index,
                    'Weight': [f"{w:.2%}" for w in latest_weights.values],
                    'Market Value': [f"${results['market_values'].iloc[-1][ticker]:,.0f}" for ticker in latest_weights.index]
                })
                st.dataframe(allocation_df, use_container_width=True)
        
        with tab3:
            st.subheader("Drawdown Analysis")
            if 'SMIF' in results['returns'].columns and 'VTI' in results['returns'].columns:
                _, _, dd = calcPerfStats(results['returns'][['SMIF', 'VTI']])
                st.line_chart(dd[['SMIF', 'VTI']], height=400)
        
        with tab4:
            st.subheader("📊 Data Export Hub")
            st.write("Export your data for advanced analysis in Jupyter, Colab, Excel, or Google Sheets")
            
            # Initialize exporter
            metadata = data_manager.get_metadata() or {}
            exporter = SMIFDataExporter(results, metadata)
            
            # Export format selection
            st.subheader("🎯 Choose Export Format")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 **For Excel/Spreadsheet Analysis**")
                
                # Excel workbook download
                excel_data = exporter.to_excel_workbook()
                st.download_button(
                    label="📗 Download Excel Workbook",
                    data=excel_data,
                    file_name=f"SMIF_Analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Complete dataset in Excel format with multiple sheets"
                )
                
                # CSV package download
                csv_package = exporter.to_csv_package()
                st.download_button(
                    label="📦 Download CSV Package",
                    data=csv_package,
                    file_name=f"SMIF_Data_{datetime.now().strftime('%Y%m%d')}.zip",
                    mime="application/zip",
                    help="ZIP file containing all data as separate CSV files"
                )
            
            with col2:
                st.markdown("### 🐍 **For Python/Jupyter Analysis**")
                
                # Pickle data download
                pickle_data = exporter.to_pickle_data()
                st.download_button(
                    label="🥒 Download Python Data (Pickle)",
                    data=pickle_data,
                    file_name=f"smif_data_{datetime.now().strftime('%Y%m%d')}.pkl",
                    mime="application/octet-stream",
                    help="Python objects for direct loading in Jupyter/Colab"
                )
                
                # JSON download
                json_data = exporter.to_json_package()
                st.download_button(
                    label="📄 Download JSON Data",
                    data=json_data,
                    file_name=f"smif_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    help="JSON format for web applications or other tools"
                )
            
            st.markdown("---")
            
            # Jupyter/Colab integration
            st.subheader("🚀 Jupyter/Colab Integration")
            
            tab_jupyter, tab_colab = st.tabs(["📓 Jupyter Notebook", "🔬 Google Colab"])
            
            with tab_jupyter:
                st.markdown("### Download Analysis Template")
                
                # Download notebook template
                notebook_json = exporter.get_jupyter_notebook()
                st.download_button(
                    label="📓 Download Jupyter Notebook Template",
                    data=notebook_json,
                    file_name="SMIF_Analysis_Template.ipynb",
                    mime="application/json",
                    help="Pre-built notebook with advanced analysis code"
                )
                
                st.markdown("**Instructions:**")
                st.markdown("1. Download the notebook template above")
                st.markdown("2. Download the pickle data file")
                st.markdown("3. Upload both to your Jupyter environment")
                st.markdown("4. Run the notebook for advanced analysis")
            
            with tab_colab:
                st.markdown("### Google Colab Setup")
                
                # Colab code
                colab_code = exporter.get_colab_code()
                st.code(colab_code, language='python')
                
                st.markdown("**Quick Start:**")
                st.markdown("1. Copy the code above into a new Colab notebook")
                st.markdown("2. Download the pickle data file from this dashboard")
                st.markdown("3. Upload the data file to Colab using `files.upload()`")
                st.markdown("4. Run the analysis functions")
                
                # Generate Colab link
                colab_url = "https://colab.research.google.com/github/googlecolab/colabtools/blob/master/notebooks/colab-github-demo.ipynb"
                st.markdown(f"🔗 [Open in Google Colab]({colab_url})")
            
            st.markdown("---")
            
            # Quick data preview
            st.subheader("👀 Quick Data Preview")
            
            preview_tabs = st.tabs(["📈 Returns", "💰 Positions", "⚖️ Weights", "📊 Summary"])
            
            with preview_tabs[0]:
                if not results['returns'].empty:
                    st.dataframe(results['returns'].tail(10).round(4), use_container_width=True)
            
            with preview_tabs[1]:
                if not results['positions'].empty:
                    st.dataframe(results['positions'].tail(5).round(2), use_container_width=True)
            
            with preview_tabs[2]:
                if not results['weights'].empty:
                    latest_weights = results['weights'].iloc[-1]
                    latest_weights = latest_weights[latest_weights > 0.01].sort_values(ascending=False)
                    st.dataframe(latest_weights.to_frame('Weight').round(3), use_container_width=True)
            
            with preview_tabs[3]:
                if not results['portfolio_summary'].empty:
                    st.dataframe(results['portfolio_summary'].tail(5).round(2), use_container_width=True)
    
    else:
        st.info("👆 Please upload the required Excel files to generate reports.")

if __name__ == "__main__":
    main()