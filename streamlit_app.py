import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy import stats
import io
import base64
from datetime import datetime
import hashlib
import data_manager
from data_exporter import SMIFDataExporter
import logging
from github_storage import GitHubStorage, get_cached_data_from_github, clear_github_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Class period configuration
        CLASS_START_DATE = st.secrets['class_period'].get('CLASS_START_DATE', '2023-09-14')  # Match portfolio start
        CLASS_END_DATE = st.secrets['class_period'].get('CLASS_END_DATE', None)  # None means current date
        CLASS_SEMESTER = st.secrets['class_period'].get('CLASS_SEMESTER', 'Current Semester')
        CLASS_INITIAL_VALUE = st.secrets['class_period'].get('CLASS_INITIAL_VALUE', INITIAL_PORTFOLIO_VALUE)
        CLASS_BENCHMARK = st.secrets['class_period'].get('CLASS_BENCHMARK', 'VTI')
        
        # GitHub storage configuration
        GITHUB_TOKEN = st.secrets.get('github', {}).get('GITHUB_TOKEN', None)
        GITHUB_DATA_REPO = st.secrets.get('github', {}).get('DATA_REPO', None)
        USE_GITHUB_STORAGE = GITHUB_TOKEN is not None and GITHUB_DATA_REPO is not None
    else:
        # Fallback to config.py for legacy support (will be deprecated)
        from config import ALLOWED_EMAILS, CLASS_PASSWORD, APP_TITLE, INITIAL_PORTFOLIO_VALUE
        st.warning("⚠️ Using legacy config.py. Please migrate to Streamlit secrets for production deployment.")
        # Default class period settings for legacy mode
        CLASS_START_DATE = '2023-09-14'  # Match the actual portfolio start date
        CLASS_END_DATE = None
        CLASS_SEMESTER = 'Current Semester'
        CLASS_INITIAL_VALUE = INITIAL_PORTFOLIO_VALUE
        CLASS_BENCHMARK = 'VTI'
        
        # GitHub storage disabled in legacy mode
        GITHUB_TOKEN = None
        GITHUB_DATA_REPO = None
        USE_GITHUB_STORAGE = False
except (ImportError, KeyError):
    # Demo configuration for testing
    st.error("⚠️ Configuration not found! Please set up .streamlit/secrets.toml or config.py")
    st.info("Demo mode: Use 'demo@university.edu' / 'demo123' to test")
    ALLOWED_EMAILS = ["demo@university.edu"]
    CLASS_PASSWORD = "demo123"
    APP_TITLE = "SMIF Dashboard (Demo Mode)"
    INITIAL_PORTFOLIO_VALUE = 338400
    # Default class period settings for demo mode
    CLASS_START_DATE = '2023-09-14'  # Match the actual portfolio start date
    CLASS_END_DATE = None
    CLASS_SEMESTER = 'Demo Semester'
    CLASS_INITIAL_VALUE = INITIAL_PORTFOLIO_VALUE
    CLASS_BENCHMARK = 'VTI'
    
    # GitHub storage disabled in demo mode
    GITHUB_TOKEN = None
    GITHUB_DATA_REPO = None
    USE_GITHUB_STORAGE = False

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

def importMonthlyData(market, years=5):
    """Import monthly data from Yahoo Finance for Treynor-Black analysis"""
    try:
        end_date = pd.to_datetime('today')
        start_date = end_date - pd.DateOffset(years=years)
        
        # Download data
        datax = yf.download(market, interval='1mo', start=start_date, end=end_date, actions=True)
        
        if datax.empty:
            return None
            
        datax.index = pd.DatetimeIndex(datax.index)
        
        # Calculate monthly returns using adjusted close
        datax['Monthly_Return'] = datax['Adj Close'].pct_change()
        
        return datax['Monthly_Return'].dropna()
        
    except Exception as e:
        return None

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

def calculate_portfolio_nav(smifPort, initV, start_date):
    """Calculate NAV starting from a specific date with specific initial value"""
    # Filter portfolio data from start_date
    port_filtered = smifPort.loc[start_date:]
    
    # Calculate NAV starting from the specified initial value
    nav = port_filtered['MktValue'] + port_filtered['Cost'].cumsum() + port_filtered['Cash'].cumsum()
    
    # Adjust to start with the specified initial value
    if len(nav) > 0:
        nav_adjustment = initV - nav.iloc[0]
        nav = nav + nav_adjustment
    
    return nav

def calculate_treynor_black_weights(port_mkts, years=5):
    """Calculate Treynor-Black model target weights using monthly data"""
    
    # Download VTI monthly data first
    vti_returns = importMonthlyData('VTI', years)
    if vti_returns is None or len(vti_returns) < 12:
        return None, "Insufficient VTI data for analysis"
    
    # Initialize results dictionary
    tb_results = {
        'ticker': [],
        'alpha': [],
        'beta': [],
        'mse': [],
        'alpha_mse': [],
        'raw_weight': [],
        'normalized_weight': []
    }
    
    # Calculate statistics for each stock
    valid_tickers = []
    for ticker in port_mkts:
        if ticker == 'NTPXX':  # Skip money market fund
            continue
            
        # Download monthly returns
        stock_returns = importMonthlyData(ticker, years)
        
        if stock_returns is None or len(stock_returns) < 12:
            continue
        
        # Align the data
        aligned_data = pd.DataFrame({
            'stock': stock_returns,
            'vti': vti_returns
        }).dropna()
        
        if len(aligned_data) < 12:  # Need at least 12 months
            continue
        
        # Run regression
        x = aligned_data['vti'].values
        y = aligned_data['stock'].values
        
        try:
            # Use scipy's linregress for simple linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Extract statistics
            alpha = intercept * 12  # Annualize alpha (monthly to annual)
            beta = slope
            
            # Calculate MSE from residuals
            y_pred = intercept + slope * x
            residuals = y - y_pred
            mse = np.mean(residuals ** 2)
            
            # Calculate alpha/MSE ratio
            alpha_mse = alpha / mse if mse > 0 else 0
            
            tb_results['ticker'].append(ticker)
            tb_results['alpha'].append(alpha)
            tb_results['beta'].append(beta)
            tb_results['mse'].append(mse)
            tb_results['alpha_mse'].append(alpha_mse)
            tb_results['raw_weight'].append(alpha_mse)
            
            valid_tickers.append(ticker)
            
        except Exception as e:
            continue
    
    # Calculate normalized weights
    if tb_results['raw_weight']:
        # Only consider positive alpha/MSE ratios for long positions
        positive_weights = [max(0, w) for w in tb_results['raw_weight']]
        total_positive = sum(positive_weights)
        
        if total_positive > 0:
            tb_results['normalized_weight'] = [w / total_positive for w in positive_weights]
        else:
            # If no positive weights, equal weight
            n = len(tb_results['ticker'])
            tb_results['normalized_weight'] = [1.0 / n] * n
    
    # Create DataFrame
    tb_df = pd.DataFrame(tb_results)
    
    # Sort by normalized weight descending
    tb_df = tb_df.sort_values('normalized_weight', ascending=False)
    
    # Calculate covariance matrix of returns
    returns_data = pd.DataFrame()
    for ticker in valid_tickers:
        stock_returns = importMonthlyData(ticker, years)
        if stock_returns is not None:
            returns_data[ticker] = stock_returns
    
    # Align all returns
    returns_data = returns_data.dropna()
    
    # Calculate covariance matrix (annualized)
    cov_matrix = returns_data.cov() * 12  # Annualize covariance
    
    return tb_df, cov_matrix

def process_smif_data(transaction_file, income_file):
    """Process SMIF data and generate reports for both inception-to-date and class period"""
    
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
            progress_bar.progress(0.5 + (i / len(portMkts)) * 0.2)
        
        # Only keep dates where we have data for at least one stock
        # This prevents losing all data if one stock has missing values
        df_rtn = df_rtn.dropna(how='all')
        df_close = df_close.loc[df_rtn.index, :]
        df_splits.fillna(0, inplace=True)
        
        # Process transactions
        status_text.text('Processing transactions...')
        progress_bar.progress(0.7)
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
        progress_bar.progress(0.8)
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
        smifPort.loc['2023-09-14','Cash'] = INITIAL_PORTFOLIO_VALUE
        
        # Calculate inception-to-date NAV and returns
        status_text.text('Calculating inception-to-date performance...')
        progress_bar.progress(0.85)
        inception_nav = calculate_portfolio_nav(smifPort, INITIAL_PORTFOLIO_VALUE, '2023-09-14')
        inception_returns = inception_nav.pct_change()
        inception_returns.fillna(0, inplace=True)
        inception_returns = pd.DataFrame(inception_returns.values, columns=['SMIF'], index=pd.DatetimeIndex(inception_returns.index))
        
        # Calculate class period NAV and returns
        status_text.text('Calculating class period performance...')
        progress_bar.progress(0.9)
        class_start_dt = pd.to_datetime(CLASS_START_DATE)
        class_end_dt = pd.to_datetime(CLASS_END_DATE) if CLASS_END_DATE else pd.to_datetime('today')
        
        # Find the closest available date to class start
        available_dates = inception_nav.index
        
        # Safety check: ensure we have data for the requested period
        if class_start_dt > available_dates[-1]:
            # Class start is after all available data - use the last available date
            class_start_actual = available_dates[-1]
            st.warning(f"⚠️ Class start date ({CLASS_START_DATE}) is after available data. Using {class_start_actual.strftime('%Y-%m-%d')} instead.")
        elif class_start_dt < available_dates[0]:
            # Class start is before available data - use the first available date
            class_start_actual = available_dates[0]
            st.warning(f"⚠️ Class start date ({CLASS_START_DATE}) is before available data. Using {class_start_actual.strftime('%Y-%m-%d')} instead.")
        else:
            # Find the closest business day on or after class start
            future_dates = available_dates[available_dates >= class_start_dt]
            class_start_actual = future_dates[0] if len(future_dates) > 0 else available_dates[-1]
        
        try:
            class_nav = calculate_portfolio_nav(smifPort, CLASS_INITIAL_VALUE, class_start_actual)
            class_returns = class_nav.pct_change()
            class_returns.fillna(0, inplace=True)
            class_returns = pd.DataFrame(class_returns.values, columns=['SMIF'], index=pd.DatetimeIndex(class_returns.index))
        except Exception as e:
            st.error(f"Error calculating class period performance: {str(e)}")
            # Fallback to inception data
            class_nav = inception_nav.copy()
            class_returns = inception_returns.copy()
            class_start_actual = available_dates[0]
        
        # Filter class period data
        class_end_actual = min(class_end_dt, available_dates[-1])
        class_mask = (class_returns.index >= class_start_actual) & (class_returns.index <= class_end_actual)
        class_returns_filtered = class_returns.loc[class_mask]
        class_nav_filtered = class_nav.loc[class_mask]
        
        # Combine with benchmark returns for both periods
        status_text.text('Combining with benchmark data...')
        progress_bar.progress(0.95)
        
        # Inception-to-date analysis
        inception_combined = inception_returns.join(df_rtn, how='outer')
        inception_combined = inception_combined.iloc[1:, :]  # Start from second day
        inception_combined = inception_combined.fillna(0)
        inception_nav_combined = (1+inception_combined).cumprod()
        
        # Class period analysis  
        class_combined = class_returns_filtered.join(df_rtn.loc[class_returns_filtered.index], how='outer')
        class_combined = class_combined.iloc[1:, :] if len(class_combined) > 1 else class_combined  # Start from second day
        class_combined = class_combined.fillna(0)
        class_nav_combined = (1+class_combined).cumprod()
        
        # Create masks for positions, weights, and market values (which have different indices)
        # Ensure we have valid data before creating masks
        try:
            positions_mask = (positions.index >= class_start_actual) & (positions.index <= class_end_actual)
            weights_mask = (weights.index >= class_start_actual) & (weights.index <= class_end_actual)
            mktvalue_mask = (MktValue.index >= class_start_actual) & (MktValue.index <= class_end_actual)
        except Exception as e:
            st.warning(f"Issue with class period filtering: {str(e)}. Using full dataset.")
            # Create empty masks as fallback
            positions_mask = pd.Series([False] * len(positions), index=positions.index)
            weights_mask = pd.Series([False] * len(weights), index=weights.index)
            mktvalue_mask = pd.Series([False] * len(MktValue), index=MktValue.index)
        
        progress_bar.progress(1.0)
        status_text.text('Analysis complete!')
        
        return {
            # Inception-to-date data
            'returns': inception_combined,
            'nav': inception_nav_combined,
            'positions': positions,
            'market_values': MktValue,
            'weights': weights,
            'portfolio_summary': smifPort,
            'trade_costs': tradeCosts,
            'port_mkts': portMkts,
            
            # Class period data
            'class_returns': class_combined,
            'class_nav': class_nav_combined,
            'class_start_date': class_start_actual,
            'class_end_date': class_end_actual,
            'class_semester': CLASS_SEMESTER,
            'class_initial_value': CLASS_INITIAL_VALUE,
            
            # Filter class period positions and weights with appropriate masks
            'class_positions': positions.loc[positions_mask] if any(positions_mask) else positions.iloc[:0],
            'class_weights': weights.loc[weights_mask] if any(weights_mask) else weights.iloc[:0],
            'class_market_values': MktValue.loc[mktvalue_mask] if any(mktvalue_mask) else MktValue.iloc[:0],
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
    if 'results' not in st.session_state:
        # Try GitHub storage first
        if USE_GITHUB_STORAGE:
            try:
                # Show loading indicator
                with st.spinner('Loading data from GitHub...'):
                    transaction_data, income_data, github_metadata = get_cached_data_from_github(GITHUB_TOKEN, GITHUB_DATA_REPO)
                    
                    if transaction_data and income_data:
                        # Process the data
                        transaction_file = io.BytesIO(transaction_data)
                        income_file = io.BytesIO(income_data)
                        
                        results = process_smif_data(transaction_file, income_file)
                        if results:
                            st.session_state['results'] = results
                            st.session_state['data_source'] = 'github'
                            st.session_state['github_metadata'] = github_metadata
                            # Store file sizes for metadata display
                            st.session_state['github_file_sizes'] = {
                                'transaction': len(transaction_data),
                                'income': len(income_data)
                            }
                            logger.info("Successfully loaded data from GitHub")
                    else:
                        st.warning("No data found in GitHub repository. Please upload new files.")
            except Exception as e:
                logger.error(f"Error loading from GitHub: {e}")
                st.error(f"Error loading from GitHub: {str(e)}")
        
        # Fall back to local data manager if no GitHub data
        if 'results' not in st.session_state and data_manager.data_exists():
            st.session_state['results'] = data_manager.load_processed_data()
            st.session_state['data_source'] = 'local'
    
    # Data overview section
    # Use GitHub metadata if available, otherwise local metadata
    if st.session_state.get('data_source') == 'github' and 'github_metadata' in st.session_state:
        github_metadata = st.session_state['github_metadata']
        if github_metadata and 'last_upload' in github_metadata:
            # Convert GitHub metadata to match local format
            # Create a full metadata structure that matches what the app expects
            metadata = {
                'last_updated': github_metadata['last_upload']['updated_at'],
                'uploaded_by': github_metadata['last_upload']['uploader'],
                'data_source': 'GitHub Repository',
                'file_info': {
                    'transaction_file': {
                        'name': 'transaction_data.xlsx',
                        'size': st.session_state.get('github_file_sizes', {}).get('transaction', 0)
                    },
                    'income_file': {
                        'name': 'income_data.xlsx', 
                        'size': st.session_state.get('github_file_sizes', {}).get('income', 0)
                    }
                },
                'portfolio_summary': {
                    'tickers': [],
                    'num_positions': 0,
                    'date_range': {
                        'start': None,
                        'end': None
                    }
                }
            }
            # Update portfolio summary from results if available
            if 'results' in st.session_state:
                if 'port_mkts' in st.session_state['results']:
                    metadata['portfolio_summary']['tickers'] = st.session_state['results']['port_mkts']
                    metadata['portfolio_summary']['num_positions'] = len(st.session_state['results']['port_mkts'])
                    
                    # Add date range from portfolio_summary data
                    if 'portfolio_summary' in st.session_state['results'] and not st.session_state['results']['portfolio_summary'].empty:
                        portfolio_data = st.session_state['results']['portfolio_summary']
                        metadata['portfolio_summary']['date_range']['start'] = portfolio_data.index[0].isoformat()
                        metadata['portfolio_summary']['date_range']['end'] = portfolio_data.index[-1].isoformat()
        else:
            metadata = None
    else:
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
            if 'results' in st.session_state and 'port_mkts' in st.session_state['results']:
                num_positions = len(st.session_state['results']['port_mkts'])
            else:
                num_positions = metadata.get('portfolio_summary', {}).get('num_positions', 'N/A')
            st.metric("Portfolio Positions", num_positions)
        
        with col3:
            st.metric(
                "Uploaded By",
                metadata['uploaded_by'].split('@')[0] if '@' in metadata['uploaded_by'] else metadata['uploaded_by']
            )
        
        # Show data source indicator if using GitHub
        if USE_GITHUB_STORAGE and st.session_state.get('data_source') == 'github':
            st.info("📦 Data loaded from GitHub repository")
        elif st.session_state.get('data_source') == 'local':
            st.info("💾 Data loaded from local storage")
        
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
            if USE_GITHUB_STORAGE:
                # Clear GitHub cache
                clear_github_cache()
            else:
                # Clear local data
                data_manager.delete_data()
            
            # Clear session state
            for key in ['results', 'data_source', 'github_metadata', 'github_file_sizes']:
                if key in st.session_state:
                    del st.session_state[key]
            
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
                        if USE_GITHUB_STORAGE:
                            try:
                                # Save to GitHub
                                storage = GitHubStorage(GITHUB_TOKEN, GITHUB_DATA_REPO)
                                
                                # Read file contents
                                transaction_file.seek(0)
                                transaction_data = transaction_file.read()
                                income_file.seek(0)
                                income_data = income_file.read()
                                
                                # Upload to GitHub
                                success = storage.upload_files(
                                    transaction_data,
                                    income_data,
                                    st.session_state.get('user_email', 'unknown')
                                )
                                
                                if success:
                                    # Clear cache to force reload
                                    clear_github_cache()
                                    st.session_state['results'] = results
                                    st.session_state['data_source'] = 'github'
                                    st.success("✅ Reports generated and saved to GitHub successfully!")
                                    logger.info("Data saved to GitHub successfully")
                                else:
                                    st.error("Failed to save to GitHub. Data processed but not persisted.")
                            except Exception as e:
                                logger.error(f"GitHub upload error: {e}")
                                st.error(f"GitHub upload error: {str(e)}")
                                # Fall back to local storage
                                data_manager.save_processed_data(results, upload_info)
                                st.session_state['results'] = results
                                st.session_state['data_source'] = 'local'
                                st.warning("Data saved locally as fallback.")
                        else:
                            # Use local data manager
                            data_manager.save_processed_data(results, upload_info)
                            st.session_state['results'] = results
                            st.session_state['data_source'] = 'local'
                            st.success("✅ Reports generated and saved successfully!")
                        
                        st.balloons()
    
    # Display results section
    if 'results' in st.session_state:
        st.markdown("---")
        st.header("📈 Performance Analysis")
        
        results = st.session_state['results']
        
        # Time period selector
        period_col1, period_col2 = st.columns([2, 1])
        with period_col1:
            analysis_period = st.selectbox(
                "📅 Analysis Period",
                ["Class Period", "Inception to Date"],
                help=f"Choose between class period ({results.get('class_semester', 'Current Semester')}) or full inception-to-date analysis"
            )
        
        with period_col2:
            if analysis_period == "Class Period" and 'class_start_date' in results:
                st.info(f"📚 **{results['class_semester']}**\n\n"
                       f"From: {results['class_start_date'].strftime('%Y-%m-%d')}\n\n"
                       f"To: {results['class_end_date'].strftime('%Y-%m-%d')}")
            elif analysis_period == "Inception to Date":
                st.info(f"📈 **Full Portfolio History**\n\n"
                       f"From: 2023-09-14\n\n"
                       f"To: {results['nav'].index[-1].strftime('%Y-%m-%d')}")
        
        # Select data based on period
        if analysis_period == "Class Period" and 'class_returns' in results and not results['class_returns'].empty:
            current_returns = results['class_returns']
            current_nav = results['class_nav']
            current_weights = results['class_weights'] if not results['class_weights'].empty else results['weights']
            current_positions = results['class_positions'] if not results['class_positions'].empty else results['positions']
            period_label = results['class_semester']
        else:
            current_returns = results['returns']
            current_nav = results['nav']
            current_weights = results['weights']
            current_positions = results['positions']
            period_label = "Inception to Date"
        
        # Performance metrics
        st.subheader(f"📊 Key Metrics - {period_label}")
        col1, col2, col3, col4 = st.columns(4)
        
        if 'SMIF' in current_returns.columns and 'VTI' in current_returns.columns and len(current_returns) > 1:
            perf_stats, _, dd = calcPerfStats(current_returns[['SMIF', 'VTI']])
            
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
        else:
            st.warning("⚠️ Insufficient data for the selected period. Please choose a different time range or upload more recent data.")
        
        # Charts
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "🥧 Allocation", "📉 Drawdown", "📋 Data"])
        
        with tab1:
            st.subheader(f"Cumulative Performance vs VTI - {period_label}")
            if 'SMIF' in current_nav.columns and 'VTI' in current_nav.columns and len(current_nav) > 1:
                chart_data = current_nav[['SMIF', 'VTI']].copy()
                st.line_chart(chart_data, height=400)
                
                # Add comparison view option
                if analysis_period == "Class Period" and 'returns' in results:
                    if st.checkbox("📈 Compare with Inception-to-Date Performance"):
                        st.subheader("Performance Comparison: Class Period vs Inception-to-Date")
                        
                        # Create comparison chart
                        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
                        
                        # Class period chart
                        ax1.plot(current_nav.index, current_nav['SMIF'], label='SMIF', linewidth=2)
                        ax1.plot(current_nav.index, current_nav['VTI'], label='VTI', linewidth=2)
                        ax1.set_title(f'{period_label} Performance')
                        ax1.set_ylabel('Cumulative Return')
                        ax1.legend()
                        ax1.grid(True, alpha=0.3)
                        
                        # Inception-to-date chart
                        ax2.plot(results['nav'].index, results['nav']['SMIF'], label='SMIF', linewidth=2)
                        ax2.plot(results['nav'].index, results['nav']['VTI'], label='VTI', linewidth=2)
                        ax2.set_title('Inception-to-Date Performance')
                        ax2.set_ylabel('Cumulative Return')
                        ax2.legend()
                        ax2.grid(True, alpha=0.3)
                        
                        plt.tight_layout()
                        st.pyplot(fig)
            else:
                st.warning("⚠️ Insufficient data for performance chart in the selected period.")
            
            # Regression analysis
            if 'SMIF' in current_returns.columns and 'VTI' in current_returns.columns and len(current_returns) > 5:
                st.subheader(f"SMIF vs VTI Regression - {period_label}")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                x_data = current_returns['VTI']
                y_data = current_returns['SMIF']
                
                ax.scatter(x_data, y_data, alpha=0.6)
                
                # Fit regression line
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)
                fitted_values = intercept + slope * x_data
                ax.plot(x_data, fitted_values, 'r-', linewidth=2, label=f'Alpha: {intercept:.4f}')
                
                ax.set_xlabel('VTI Returns')
                ax.set_ylabel('SMIF Returns')
                ax.set_title(f'SMIF vs VTI Scatter Plot - {period_label}')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                st.pyplot(fig)
                
                # Display regression stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Alpha", f"{intercept:.4f}")
                with col2:
                    st.metric("Beta", f"{slope:.4f}")
                with col3:
                    st.metric("R-squared", f"{r_value**2:.3f}")
            else:
                st.warning("⚠️ Insufficient data for regression analysis in the selected period (minimum 5 observations required).")
        
        with tab2:
            st.subheader(f"Portfolio Allocation - {period_label}")
            if not current_weights.empty:
                latest_weights = current_weights.iloc[-1]
                latest_weights = latest_weights[latest_weights > 0].sort_values(ascending=False)
                
                # Pie chart
                fig, ax = plt.subplots(figsize=(10, 8))
                ax.pie(latest_weights.values, labels=latest_weights.index, autopct='%1.1f%%', startangle=90)
                ax.set_title(f'Portfolio Allocation - {period_label}')
                st.pyplot(fig)
                
                # Table
                st.subheader("Allocation Details")
                # Use the appropriate market values based on period
                if analysis_period == "Class Period" and 'class_market_values' in results and not results['class_market_values'].empty:
                    market_vals = results['class_market_values'].iloc[-1]
                else:
                    market_vals = results['market_values'].iloc[-1]
                
                allocation_df = pd.DataFrame({
                    'Ticker': latest_weights.index,
                    'Weight': [f"{w:.2%}" for w in latest_weights.values],
                    'Market Value': [f"${market_vals[ticker]:,.0f}" if ticker in market_vals.index else "N/A" for ticker in latest_weights.index]
                })
                st.dataframe(allocation_df, use_container_width=True)
                
                # Period comparison for allocation
                if analysis_period == "Class Period" and st.checkbox("📊 Compare Allocation Over Time"):
                    st.subheader("Allocation Evolution During Class Period")
                    
                    # Create time series of top holdings
                    top_tickers = latest_weights.head(5).index.tolist()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    
                    for ticker in top_tickers:
                        if ticker in current_weights.columns:
                            ax.plot(current_weights.index, current_weights[ticker], label=ticker, linewidth=2)
                    
                    ax.set_title(f'Top 5 Holdings Weight Evolution - {period_label}')
                    ax.set_ylabel('Portfolio Weight')
                    ax.set_xlabel('Date')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # Treynor-Black Model Target Allocation
                st.markdown("---")
                st.subheader("🎯 Treynor-Black Model Target Allocation")
                st.write("Optimal portfolio weights based on 5 years of monthly data using alpha/MSE ratios")
                
                if 'port_mkts' in results:
                    with st.spinner('Calculating Treynor-Black weights...'):
                        tb_weights, cov_matrix = calculate_treynor_black_weights(results['port_mkts'])
                        
                        if tb_weights is not None and not tb_weights.empty:
                            # Display metrics
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    "Stocks Analyzed", 
                                    len(tb_weights),
                                    help="Number of stocks with sufficient data for analysis"
                                )
                            
                            with col2:
                                positive_alpha = (tb_weights['alpha'] > 0).sum()
                                st.metric(
                                    "Positive Alpha Stocks", 
                                    positive_alpha,
                                    help="Stocks with positive alpha vs VTI"
                                )
                            
                            with col3:
                                # Portfolio beta (weighted average)
                                portfolio_beta = (tb_weights['beta'] * tb_weights['normalized_weight']).sum()
                                st.metric(
                                    "Target Portfolio Beta", 
                                    f"{portfolio_beta:.2f}",
                                    help="Weighted average beta of target portfolio"
                                )
                            
                            # Display the weights table
                            st.subheader("Target Weights Analysis")
                            
                            # Format the dataframe for display
                            display_df = tb_weights.copy()
                            display_df['Alpha (Annual)'] = display_df['alpha'].apply(lambda x: f"{x:.2%}")
                            display_df['Beta'] = display_df['beta'].apply(lambda x: f"{x:.3f}")
                            display_df['MSE'] = display_df['mse'].apply(lambda x: f"{x:.4f}")
                            display_df['Alpha/MSE'] = display_df['alpha_mse'].apply(lambda x: f"{x:.4f}")
                            display_df['Target Weight'] = display_df['normalized_weight'].apply(lambda x: f"{x:.2%}")
                            
                            # Compare with current weights
                            current_weight_dict = latest_weights.to_dict()
                            display_df['Current Weight'] = display_df['ticker'].apply(
                                lambda x: f"{current_weight_dict.get(x, 0):.2%}"
                            )
                            display_df['Weight Difference'] = display_df.apply(
                                lambda row: f"{row['normalized_weight'] - current_weight_dict.get(row['ticker'], 0):.2%}", 
                                axis=1
                            )
                            
                            # Select columns to display
                            columns_to_show = ['ticker', 'Alpha (Annual)', 'Beta', 'MSE', 'Alpha/MSE', 
                                             'Target Weight', 'Current Weight', 'Weight Difference']
                            
                            st.dataframe(
                                display_df[columns_to_show],
                                use_container_width=True,
                                height=400
                            )
                            
                            # Visualization of target vs current weights
                            if len(tb_weights) > 0:
                                st.subheader("Target vs Current Allocation Comparison")
                                
                                # Prepare data for comparison chart
                                comparison_tickers = tb_weights['ticker'].tolist()
                                target_weights = tb_weights['normalized_weight'].tolist()
                                current_weights_list = [current_weight_dict.get(ticker, 0) for ticker in comparison_tickers]
                                
                                # Create comparison bar chart
                                fig, ax = plt.subplots(figsize=(12, 6))
                                
                                x = np.arange(len(comparison_tickers))
                                width = 0.35
                                
                                bars1 = ax.bar(x - width/2, current_weights_list, width, label='Current', alpha=0.8)
                                bars2 = ax.bar(x + width/2, target_weights, width, label='Treynor-Black Target', alpha=0.8)
                                
                                ax.set_xlabel('Stock')
                                ax.set_ylabel('Portfolio Weight')
                                ax.set_title('Current vs Treynor-Black Target Allocation')
                                ax.set_xticks(x)
                                ax.set_xticklabels(comparison_tickers, rotation=45, ha='right')
                                ax.legend()
                                ax.grid(True, alpha=0.3, axis='y')
                                
                                # Add percentage labels on bars
                                for bars in [bars1, bars2]:
                                    for bar in bars:
                                        height = bar.get_height()
                                        if height > 0.01:  # Only label if > 1%
                                            ax.annotate(f'{height:.1%}',
                                                      xy=(bar.get_x() + bar.get_width() / 2, height),
                                                      xytext=(0, 3),  # 3 points vertical offset
                                                      textcoords="offset points",
                                                      ha='center', va='bottom',
                                                      fontsize=8)
                                
                                plt.tight_layout()
                                st.pyplot(fig)
                            
                            # Display covariance matrix in expander
                            with st.expander("📊 View Covariance Matrix (Annualized)"):
                                st.write("Annualized covariance matrix of monthly returns")
                                
                                # Format covariance matrix for display
                                cov_display = cov_matrix.copy()
                                cov_display = cov_display.round(4)
                                
                                # Create heatmap
                                fig, ax = plt.subplots(figsize=(10, 8))
                                im = ax.imshow(cov_display.values, cmap='RdBu_r', aspect='auto')
                                
                                # Set ticks
                                ax.set_xticks(np.arange(len(cov_display.columns)))
                                ax.set_yticks(np.arange(len(cov_display.index)))
                                ax.set_xticklabels(cov_display.columns, rotation=45, ha='right')
                                ax.set_yticklabels(cov_display.index)
                                
                                # Add colorbar
                                plt.colorbar(im)
                                
                                # Add text annotations
                                for i in range(len(cov_display.index)):
                                    for j in range(len(cov_display.columns)):
                                        text = ax.text(j, i, f'{cov_display.iloc[i, j]:.3f}',
                                                     ha="center", va="center", color="black", fontsize=8)
                                
                                ax.set_title("Covariance Matrix Heatmap")
                                plt.tight_layout()
                                st.pyplot(fig)
                                
                                # Also show as dataframe
                                st.dataframe(cov_display, use_container_width=True)
                            
                            # Model insights
                            with st.expander("📚 Treynor-Black Model Insights"):
                                st.markdown("""
                                **About the Treynor-Black Model:**
                                
                                The Treynor-Black model is a portfolio optimization approach that combines:
                                - **Active portfolio:** Stocks with positive alpha (expected excess returns)
                                - **Passive portfolio:** Market index (VTI in this case)
                                
                                **Key Components:**
                                
                                1. **Alpha (α):** Expected excess return over the market
                                2. **Beta (β):** Systematic risk relative to the market
                                3. **MSE:** Mean Squared Error from regression (unsystematic risk)
                                4. **Alpha/MSE:** Information ratio used for weighting
                                
                                **Optimal Weight Formula:**
                                - Weight ∝ Alpha / MSE (higher alpha and lower residual risk = higher weight)
                                - Weights are normalized to sum to 1.0
                                
                                **Interpretation:**
                                - Stocks with higher alpha/MSE ratios receive larger allocations
                                - The model favors stocks with consistent outperformance (high alpha, low MSE)
                                - Negative or zero weights indicate stocks that should not be held
                                """)
                        else:
                            st.warning("⚠️ Unable to calculate Treynor-Black weights. Insufficient data or no valid stocks found.")
                else:
                    st.warning("⚠️ Portfolio tickers not found in results.")
            else:
                st.warning("⚠️ No allocation data available for the selected period.")
        
        with tab3:
            st.subheader(f"Drawdown Analysis - {period_label}")
            if 'SMIF' in current_returns.columns and 'VTI' in current_returns.columns and len(current_returns) > 1:
                _, _, dd = calcPerfStats(current_returns[['SMIF', 'VTI']])
                st.line_chart(dd[['SMIF', 'VTI']], height=400)
                
                # Drawdown statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("SMIF Drawdown Stats")
                    max_dd = dd['SMIF'].min()
                    current_dd = dd['SMIF'].iloc[-1]
                    st.metric("Maximum Drawdown", f"{max_dd:.2%}")
                    st.metric("Current Drawdown", f"{current_dd:.2%}")
                    
                    # Count drawdown periods
                    drawdown_periods = (dd['SMIF'] < -0.01).sum()  # Periods with >1% drawdown
                    st.metric("Days with >1% Drawdown", f"{drawdown_periods}")
                
                with col2:
                    st.subheader("VTI Drawdown Stats") 
                    max_dd_vti = dd['VTI'].min()
                    current_dd_vti = dd['VTI'].iloc[-1]
                    st.metric("Maximum Drawdown", f"{max_dd_vti:.2%}")
                    st.metric("Current Drawdown", f"{current_dd_vti:.2%}")
                    
                    drawdown_periods_vti = (dd['VTI'] < -0.01).sum()
                    st.metric("Days with >1% Drawdown", f"{drawdown_periods_vti}")
            else:
                st.warning("⚠️ Insufficient data for drawdown analysis in the selected period.")
        
        with tab4:
            st.subheader("📊 Data Export Hub")
            st.write("Export your data for advanced analysis in Jupyter, Colab, Excel, or Google Sheets")
            
            # Period selection for export
            export_period = st.selectbox(
                "📅 Export Data Period",
                ["Both Periods", "Class Period Only", "Inception-to-Date Only"],
                help="Choose which time period data to include in exports"
            )
            
            # Prepare data based on export selection
            if export_period == "Class Period Only" and 'class_returns' in results:
                export_results = {
                    'returns': results['class_returns'],
                    'nav': results['class_nav'],
                    'positions': results['class_positions'],
                    'market_values': results['class_market_values'],
                    'weights': results['class_weights'],
                    'portfolio_summary': results['portfolio_summary'],
                    'trade_costs': results['trade_costs'],
                    'port_mkts': results['port_mkts']
                }
                period_suffix = f"_{results['class_semester'].replace(' ', '_')}"
            elif export_period == "Inception-to-Date Only":
                export_results = {
                    'returns': results['returns'],
                    'nav': results['nav'],
                    'positions': results['positions'],
                    'market_values': results['market_values'],
                    'weights': results['weights'],
                    'portfolio_summary': results['portfolio_summary'],
                    'trade_costs': results['trade_costs'],
                    'port_mkts': results['port_mkts']
                }
                period_suffix = "_InceptionToDate"
            else:
                export_results = results  # Include all data
                period_suffix = "_Complete"
            
            # Initialize exporter
            metadata = data_manager.get_metadata() or {}
            # Add class period info to metadata
            if 'class_semester' in results:
                metadata['class_period'] = {
                    'semester': results['class_semester'],
                    'start_date': results['class_start_date'].strftime('%Y-%m-%d'),
                    'end_date': results['class_end_date'].strftime('%Y-%m-%d'),
                    'initial_value': results['class_initial_value']
                }
            
            exporter = SMIFDataExporter(export_results, metadata)
            
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
                    file_name=f"SMIF_Analysis{period_suffix}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help=f"Complete dataset in Excel format ({export_period.lower()})"
                )
                
                # CSV package download
                csv_package = exporter.to_csv_package()
                st.download_button(
                    label="📦 Download CSV Package",
                    data=csv_package,
                    file_name=f"SMIF_Data{period_suffix}_{datetime.now().strftime('%Y%m%d')}.zip",
                    mime="application/zip",
                    help=f"ZIP file containing data as separate CSV files ({export_period.lower()})"
                )
            
            with col2:
                st.markdown("### 🐍 **For Python/Jupyter Analysis**")
                
                # Pickle data download
                pickle_data = exporter.to_pickle_data()
                st.download_button(
                    label="🥒 Download Python Data (Pickle)",
                    data=pickle_data,
                    file_name=f"smif_data{period_suffix}_{datetime.now().strftime('%Y%m%d')}.pkl",
                    mime="application/octet-stream",
                    help=f"Python objects for direct loading in Jupyter/Colab ({export_period.lower()})"
                )
                
                # JSON download
                json_data = exporter.to_json_package()
                st.download_button(
                    label="📄 Download JSON Data",
                    data=json_data,
                    file_name=f"smif_data{period_suffix}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    help=f"JSON format for web applications or other tools ({export_period.lower()})"
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
            st.subheader(f"👀 Quick Data Preview - {export_period}")
            
            preview_tabs = st.tabs(["📈 Returns", "💰 Positions", "⚖️ Weights", "📊 Summary"])
            
            with preview_tabs[0]:
                if not export_results['returns'].empty:
                    preview_returns = export_results['returns'].tail(10).round(4)
                    st.dataframe(preview_returns, use_container_width=True)
                    if export_period == "Both Periods" and 'class_returns' in results:
                        st.caption(f"Showing last 10 days of inception-to-date data. Class period has {len(results['class_returns'])} observations.")
            
            with preview_tabs[1]:
                if not export_results['positions'].empty:
                    preview_positions = export_results['positions'].tail(5).round(2)
                    st.dataframe(preview_positions, use_container_width=True)
            
            with preview_tabs[2]:
                if not export_results['weights'].empty:
                    latest_weights = export_results['weights'].iloc[-1]
                    latest_weights = latest_weights[latest_weights > 0.01].sort_values(ascending=False)
                    st.dataframe(latest_weights.to_frame('Weight').round(3), use_container_width=True)
            
            with preview_tabs[3]:
                if not export_results['portfolio_summary'].empty:
                    preview_summary = export_results['portfolio_summary'].tail(5).round(2)
                    st.dataframe(preview_summary, use_container_width=True)
    
    else:
        st.info("👆 Please upload the required Excel files to generate reports.")

if __name__ == "__main__":
    main()