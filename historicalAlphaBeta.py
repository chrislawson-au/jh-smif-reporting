import pandas as pd
import yfinance as yf
import statsmodels.api as sm

# default lookback window is set to be 10 years
# the last ticker symbol in the list of portfolio markets must be the benchmark
def importYahooData(market, startdate='2014-01-01', enddate=None):
    datax = yf.download(market, interval='1d', start=startdate, end=enddate, actions=True)
    datax.index = pd.DatetimeIndex(datax.index.strftime('%Y-%m-%d'))
    datax['Close.Rtns'] = datax['Close'].pct_change()
    datax['Div.Rtns'] = datax['Dividends']/datax['Close'].shift(1)
    datax['Adj.Rtns'] = datax['Close.Rtns']+datax['Div.Rtns']
    datax['deltaClose']=datax['Close'].diff(1)+datax['Dividends']
    return datax['Close'], datax['Adj.Rtns'], datax['Stock Splits'], datax['deltaClose']

def alphaBeta(portMkts, startDate='2014-01-01', endDate=None) :
    n=len(portMkts)
    df_close = pd.DataFrame()
    df_rtn = pd.DataFrame()
    df_abe = pd.DataFrame()

    for i in range(n):
        df_close[portMkts[i]],df_rtn[portMkts[i]],*_ = importYahooData(portMkts[i], startDate)
    df_rtn = df_rtn.dropna()
    df_wRtn = (df_rtn+1).cumprod().resample('1W',label='right').last().pct_change().dropna()

    ## the last ticker symbol in portMkts is asusmed to be the benchmark ##
    benCol = portMkts[n-1]
    x = df_wRtn[benCol]
    x = sm.add_constant(x)
    for i in range(n-1):
        col= portMkts[i]
        y = df_wRtn[col]
        reg = sm.OLS(y, x).fit()
        df_abe[col]=[reg.params['const'],reg.params[benCol],reg.tvalues['const'],reg.pvalues['const'],reg.mse_resid]
    return df_abe

## the last ticker symbol in portMkts must be the benchmark
portMkts = ['NVDA', 'MAR', 'TMUS','ELF','BLDR','VTI']
df_abe = alphaBeta(portMkts,startDate='2023-09-01')
df_abe.index=['alpha','beta','t_alpha','p_alpha','mse']

df_abe.to_csv('weekly alpha beta and mse.csv')
