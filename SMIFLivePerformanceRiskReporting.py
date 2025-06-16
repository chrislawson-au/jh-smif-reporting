import numpy as np
import pandas as pd
import os
import yfinance as yf
import matplotlib
from matplotlib import pyplot as plt
import statsmodels.api as sm
####################################################################
# first, upload the brokerage reports from your local computer drive
dirpath = os.getcwd()
filepath = os.path.join(dirpath, 'Investment_Transaction_Detail_-_Customizable.xlsx')
smifReport = pd.read_excel(filepath)
filepath = os.path.join(dirpath, 'Income_and_Expense_Detail_Base_by_Account.xlsx')
smifIncome = pd.read_excel(filepath)

# then, preprocess and parse the income report
def emptyStr(x): return(str(x).strip()!='')
x = smifIncome['Recognition date'].to_list()
smif_Income=smifIncome.loc[list(map(emptyStr,x)), ['Narrative - Short','Recognition date', 'Net amount - base']]
smif_Income = smif_Income.set_index(smif_Income['Recognition date'])[['Narrative - Short','Net amount - base']]
smif_Income.index=pd.to_datetime(smif_Income.index)
smif_Income = smif_Income.groupby(['Recognition date']).apply('sum')['Net amount - base']

# get tickers for all markets included in the transaction report
portMkts = smifReport['Ticker/Option Symbol number'].tolist()
portMkts = sorted(set(portMkts),key=portMkts.index)
# remove NTPXX, which is the ticker for the money market fund
portMkts.remove('NTPXX')

############################################################################################
# now, download market data from yahoo finance, and set the dates for risk reporting period
def importYahooData(market, startdate='2023-09-01', enddate=None):
    datax = yf.download(market, interval='1d', start=startdate, end=enddate, actions=True)
    datax.index = pd.DatetimeIndex(datax.index.strftime('%Y-%m-%d'))
    datax['Close.Rtns'] = datax['Close'].pct_change()
    datax['Div.Rtns'] = datax['Dividends']/datax['Close'].shift(1)
    datax['Adj.Rtns'] = datax['Close.Rtns']+datax['Div.Rtns']
    datax['deltaClose']=datax['Close'].diff(1)+datax['Dividends']
    return datax['Close'], datax['Adj.Rtns'], datax['Stock Splits'], datax['deltaClose']

dates=pd.date_range('2023-09-01',pd.to_datetime('today').strftime('%Y-%m-%d'),freq='B')
df_close = pd.DataFrame(np.nan, columns=portMkts,index=dates)
df_rtn = pd.DataFrame(np.nan, columns=portMkts,index=dates)
df_splits = pd.DataFrame(np.nan, columns=portMkts,index=dates)
for i in range(len(portMkts)):
    df_close[portMkts[i]],df_rtn[portMkts[i]],df_splits[portMkts[i]],*_ = importYahooData(portMkts[i],'2023-09-01')

df_rtn = df_rtn.loc[np.isnan(df_rtn.sum(axis=1,skipna=False)) == False,:]
df_close = df_close.loc[df_rtn.index,:]
df_splits.fillna(0,inplace=True)

#########################################################################################
# save market data to local computer drive
df_close.to_csv('SMIF daily close prices.csv',index_label='Date',date_format='%Y-%m-%d')
df_rtn.to_csv('SMIF daily returns.csv',index_label='Date',date_format='%Y-%m-%d')
df_splits.to_csv('SMIF daily splits.csv',index_label='Date',date_format='%Y-%m-%d')

# load market data into dataframes
df_close = pd.read_csv('SMIF daily close prices.csv',index_col='Date')
df_rtn = pd.read_csv('SMIF daily returns.csv',index_col='Date')
df_splits = pd.read_csv('SMIF daily splits.csv',index_col='Date')

df_close.index = pd.DatetimeIndex(df_close.index)
df_rtn.index = pd.DatetimeIndex(df_rtn.index)
df_splits.index = pd.DatetimeIndex(df_splits.index)
##########################################################################################

# set dates for risk reporting period
dates=pd.DatetimeIndex(df_rtn['2023-09-14':].index)

##################################################################
# now, we are ready to preprocess and parse the transaction report
smifTrade = smifReport[['D-TRADE','Share/Par Value','A-PRIN-TRD-BSE','Ticker/Option Symbol number']]
smifTrade = smifTrade.groupby(['D-TRADE','Ticker/Option Symbol number']).apply('sum')
smifTrade = smifTrade.reset_index(level='Ticker/Option Symbol number')
trades = pd.DataFrame(np.nan,columns=portMkts,index=dates)
for i in trades.columns:
    trades[i] = smifTrade.loc[smifTrade['Ticker/Option Symbol number'] == i, 'Share/Par Value']
    tradeDates=trades.loc[np.isnan(trades[i])==False, i].index
    firstTrade=tradeDates[0]
    splitDates=df_splits.loc[df_splits[i]!=0,i].index

    # the code below adjusts number of shares for trades executed before splits
    if (len(splitDates) > 0):
        print(i)
        for k in splitDates:
            splitFactor = df_splits.loc[k, i]
            tradesBeforeSplit = (trades.index < k)
            trades.loc[tradesBeforeSplit, i] = splitFactor * trades.loc[tradesBeforeSplit, i]

trades.fillna(0,inplace=True)
psn=trades.cumsum()
# write the 1st report to local computer drive: positions
psn.to_csv('positions.csv',date_format='%Y-%m-%d')
# write the 2nd report to local computer drive: trade costs
smifTrade=smifTrade.loc[smifTrade['Ticker/Option Symbol number']!='NTPXX']
tradeCosts=smifTrade.groupby(['D-TRADE']).apply('sum')['A-PRIN-TRD-BSE']
tradeCosts.to_csv('tradeCosts.csv',date_format='%Y-%m-%d')

####################################################################################################
# now, move to generate market values, % allocation of capital, account net asset value, and returns
initV = 338400
MktClose = df_close.loc[psn.index,:]
MktValue = pd.DataFrame(psn[portMkts].values * MktClose[portMkts].values,columns=portMkts,index=psn.index)
# write the 3rd report to local computer: asset market values
MktValue.to_csv('mktValues.csv',date_format='%Y-%m-%d')
# write the 4th report to local computer: % allocation of capital
wts = MktValue.divide(MktValue.sum(axis=1), axis=0)
wts.to_csv('allocations.csv',date_format='%Y-%m-%d')
MktValue.tail(5).sort_values(by=MktValue.tail(1).index.strftime('%Y-%m-%d').values[0],axis=1).to_csv('sorted MktValues.csv',date_format='%Y-%m-%d')
wts.tail(5).sort_values(by=wts.tail(1).index.strftime('%Y-%m-%d').values[0],axis=1).to_csv('sorted allocations.csv',date_format='%Y-%m-%d')

# set up a dataframe smifPort that contains the three essential components of account net asset values
smifPort = pd.DataFrame(0.0, columns=['MktValue','Cost','Cash'],index=dates)
smifPort['MktValue']=MktValue.sum(axis=1)
smifPort['Cost']=tradeCosts
smifPort['Cash']=smif_Income
smifPort.fillna(0,inplace=True)
smifPort.loc['2023-09-14','Cash']=initV

# then, calculate the net asset values and returns
smifNav = smifPort['MktValue']+smifPort['Cost'].cumsum()+smifPort['Cash'].cumsum()
smifRtn = smifNav.pct_change()
smifRtn.fillna(0,inplace=True)
smifRtn=pd.DataFrame(smifRtn.values,columns=['SMIF'],index=pd.DatetimeIndex(smifRtn.index))
smifRtn.index = pd.DatetimeIndex(smifRtn.index.strftime('%Y-%m-%d'))

res = smifRtn.join(df_rtn)
res=res.iloc[1:, :]  # begin to compare returns starting on 09/15
resNav = (1+res).cumprod()

def calcPerfStats(rtns,scale=252):
    n = len(rtns.index)
    w = (1+rtns).prod()
    annRtn = w ** (scale/n) - 1
    annStd = rtns.std() * np.sqrt(scale)
    sRatio = annRtn / annStd
    nav = (1+rtns).cumprod()
    dd = nav/nav.cummax() - 1
    df = pd.DataFrame()
    for col in rtns.columns:
        df[col] = [annRtn[col],annStd[col],sRatio[col],dd.min()[col]]
    df.index=['AnnRtn','AnnStd','Sharpe','MDD']
    return df, nav, dd

matplotlib.use('TkAgg',force=True)
resNav[resNav.index>='2023-09-15'][['SMIF','VTI']].plot(figsize=(10,6),label=['SMIF','VTI'],lw=3,title='Growth of $1')

resSP25=res[res.index>='2025-01-21'] # begin to compare returns starting on 01/21
resNavSP25 = (1+resSP25).cumprod()
resNavSP25[['SMIF','VTI']].plot(figsize=(10,6),label=['SMIF','VTI'],lw=3,title='Growth of $1')
perfStats, nav, dd = calcPerfStats(resSP25)
perfStats[wts.columns[(wts.tail(1)!=0).stack()]].to_csv('SMIF Market Performances.csv')

#resNav[resNav.index>='2023-11-15'][['SMIF','VTI']].plot(figsize=(10,6),label=['SMIF','VTI'],lw=3,title='Growth of $1')
# write the plot to local computer drive
plt.savefig('SMIFvsVTI.png', bbox_inches='tight')
plt.close()

## realized information ratio
xdata=res.loc[res.index>='2023-09-15',:]
Z = xdata['VTI']
Z = sm.add_constant(Z, prepend=True)
y = xdata['SMIF']
mod = sm.OLS(y, Z).fit()
mod.summary()
mod.params
np.std(mod.resid)
mod.params['const']/np.std(mod.resid)

xdata.to_csv('SMIF Returns.csv',date_format='%Y-%m-%d')

matplotlib.use('TkAgg',force=True)
xdata.plot(figsize=(10,6),x='VTI',y='SMIF',lw=3,kind='scatter',title='SMIF vs. VTI')
plt.plot(xdata['VTI'], mod.fittedvalues, "r-", linewidth=3, label="OLS")
plt.savefig('SMIFvsVTI Regression Line.png', bbox_inches='tight')
plt.close()

perfStats, nav, dd = calcPerfStats(xdata)
# write the 5th report to local drive about the fund's performance vs. benchmark
perfStats[['SMIF','VTI']].to_csv('SMIFvsVTI Performance Stats.csv')
perfStats[wts.columns[(wts.tail(1)!=0).stack()]].to_csv('SMIF Market Performances.csv')
#perfStats.sort_values(by='Sharpe',axis=1).to_csv('SMIFvsVTI Performance Stats.csv')
matplotlib.use('TkAgg',force=True)
dd[['SMIF','VTI']].plot(title='SMIF vs. VTI: Drawdown Comparison',lw=3)
plt.savefig('SMIFvsVTI Drawdown Comparison.png', bbox_inches='tight')
plt.close()

# min(dd['SMIF'])
round(perfStats[['SMIF','VTI']],2)
######################################################################################
# Risk reporting statistics on active portion of the overall portfolio

# first, compute the alpha and beta for all active markets in the SMIF portfolio
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

## make sure that the last ticker symbol in Mkts be the benchmark
Mkts = wts.columns[(wts.tail(1)!=0).stack()].tolist()
Mkts.remove('VTI')
Mkts.append('VTI')

df_abe = alphaBeta(Mkts,startDate='2023-01-01')
df_abe.index=['alpha','beta','t_alpha','p_alpha','mse']

df_abe.to_csv('weekly alpha beta and mse.csv')

# now, compute the risk budget for each active markets in the active portion of the portfolio
activeMkts = Mkts.copy()
activeMkts.remove('VTI')

activeWts = wts[activeMkts].copy()
activeWts = activeWts.divide(activeWts.sum(axis=1), axis=0)

mktRtn = df_rtn[activeMkts]
curPsn = pd.DataFrame(np.repeat(activeWts.tail(1).values,mktRtn.shape[0],axis=0),columns=activeMkts,index=mktRtn.index)
simulatedPsnRtns = mktRtn * curPsn

portrisk = simulatedPsnRtns.sum(axis=1).std()*np.sqrt(252)
wtdVol = activeWts.tail(1).values.tolist()[0]*mktRtn.std()*np.sqrt(252)

riskReport = pd.DataFrame(columns=['Weight','Vol','wtdVol','Corr','MRC','Beta','riskBudget','riskImpact','sumWtdVol','DV'],index=activeMkts)
riskReport['Weight']=activeWts.tail(1).values.tolist()[0]
riskReport['Vol']=mktRtn.std()*np.sqrt(252)
riskReport['wtdVol']=wtdVol
riskReport['Corr']=mktRtn.corrwith(simulatedPsnRtns.sum(axis=1))
riskReport['MRC']=riskReport['Vol'] * riskReport['Corr']
riskReport['Beta']=riskReport['MRC'] / portrisk
riskReport['riskBudget']=riskReport['Beta'] * activeWts.tail(1).values.tolist()[0]
riskReport['riskImpact']=riskReport['MRC'] * activeWts.tail(1).values.tolist()[0]

new_row = pd.DataFrame({'Weight': 1, 'Vol': portrisk, 'wtdVol': portrisk, 'Corr': 1,
           'MRC': portrisk, 'Beta': 1, 'riskBudget': 1, 'riskImpact': portrisk, 'sumWtdVol': sum(wtdVol),
           'DV': sum(wtdVol) - portrisk},index=['activeP'])

riskReport = pd.concat([riskReport,new_row])
riskReport.to_csv('SMIF Active Risk Decomposition and Risk Budget.csv',float_format="%.6f")
