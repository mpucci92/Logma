from joblib import Parallel, delayed
from argparse import ArgumentParser
import pandas as pd
import numpy as np
import sys, os

from entropy import spectral_entropy, app_entropy
from statsmodels.tsa.stattools import adfuller
from scipy.stats import kurtosis

from consts import dir_

###################################

input_dir_ = 'D:/TickData_UZ'
output_dir_ = 'D:/TickData_Agg'

#Rel Vol 1-week MA
n_periods = 7
n_candles = 480

#Long/Short windows
short_window = 20
long_window = 50

n_jobs = 6

###################################

def filter_weekends(df):
    df['Datetime'] = pd.to_datetime(df.Datetime)
    df = df[~df.Datetime.dt.weekday_name.isin(['Saturday', 'Sunday'])]
    return df

def compute_relative_volume(df, n_periods, n_candles):
	
    #Align the dataset to start at a day
    idx = df.Datetime.astype(str).str.split(' ', expand=True)[1].values.tolist().index('00:00:00')
    df = df.iloc[idx:, :]
    
    cut_off = [i for i in range(0, len(df), n_candles)][-1]
    df = df.iloc[:cut_off, :]
    cumvol = np.array(np.split(df.Volume.values, int(len(df)/n_candles)))
    
    cumvol = np.cumsum(cumvol, axis=1)
    cumvol = cumvol.reshape(-1, )
    
    offset = n_periods * n_candles
    cumvol_final = [0 for i in range(offset)]
    
    for i in range(offset, len(df), n_candles):
        
        voldist = cumvol[i-offset:i]
        idc = np.arange(0, offset, n_candles)
        voldist = [voldist[idc+i].mean() for i in range(0, n_candles)]
        cumvol_final += voldist
    
    df['RelVol'] = np.divide(cumvol, cumvol_final)
    return df.iloc[offset:, :]

def approx_entropy(x):
    
    try:
        return app_entropy(x, order=2, metric='chebyshev')
    except:
        return np.nan
    
def spec_entropy(x):

    try:
        offset = x.shape[0]
        return spectral_entropy(x, sf=offset, method='welch', nperseg=(offset/8), normalize=True)
    except:
        return np.nan
    
def autocorrelation(x):
    
    try:
        return x.autocorr(11)
    except:
        return np.nan
    
def stationarity(x):
    
    try:
        t, _, _, _, t_crit = adfuller(x, autolag = 'AIC')
        t_crit = list(t_crit.values())[1]
        return 0 if (t < t_crit or np.isnan(t)) else 1
    except:
        return np.nan

def features(ticker):

	print(ticker)

	def cp(x):
		return x.cumprod()[-1]

	df = pd.read_csv('D:/TickData_Agg/{}.csv'.format(ticker))
	df = filter_weekends(df)

	df['Change'] = (df.Close - df.Open) / df.Open
	
	## Distribution Statistics
	df['STDLong'] = df.Change.rolling(window=long_window, min_periods=1).std()
	df['STDShort'] = df.Change.rolling(window=short_window, min_periods=1).std()
	
	df['LongVol'] = df.STDLong/np.sqrt(long_window)
	df['ShortVol'] = df.STDShort/np.sqrt(short_window)
	
	# Add a small quantity to avoid -inf from the logarithm
	df['LongVol'] = np.log(df.LongVol+1e-8)
	df['ShortVol'] = np.log(df.ShortVol+1e-8)

	df['LongSkew'] = df.Change.rolling(window=long_window, min_periods=1).skew()
	df['ShortSkew'] = df.Change.rolling(window=short_window, min_periods=1).skew()

	df['LongKurtosis'] = df.Change.rolling(window=long_window, min_periods=1).apply(kurtosis, raw=True)
	df['ShortKurtosis'] = df.Change.rolling(window=short_window, min_periods=1).apply(kurtosis, raw=True)

	#Positioning Indicators
	df['LongEMA'] = df.Close.ewm(span=long_window, min_periods=1).mean()
	df['ShortEMA'] = df.Close.ewm(span=short_window, min_periods=1).mean()

	df['DLongEMA'] = df.Close / df['LongEMA'].values
	df['DShortEMA'] = df.Close / df['ShortEMA'].values

	### Center Metrics Around 1
	for col in df.columns:
	    if col in ['Open', 'High', 'Low', 'Close']:
	        df[col] = df[col].pct_change() + 1

	def cp(x):
		return x.cumprod()[-1]

	df['LongSkew'] = df.LongSkew.fillna(value=0)
	df['ShortSkew'] = df.ShortSkew.fillna(value=0)

	df['LongKurtosis'] = df.LongKurtosis.fillna(value=0)
	df['ShortKurtosis'] = df.ShortKurtosis.fillna(value=0)

	# Time series progressions
	df['LongProg'] = df.Close.rolling(window=long_window, min_periods=1).apply(cp, raw=True)
	df['ShortProg'] = df.Close.rolling(window=short_window, min_periods=1).apply(cp, raw=True)

	# Approximate Entropy
	df['LongApproximateEntropy'] = df.Change.rolling(window=long_window, min_periods=1).apply(approx_entropy, raw=True)
	df['ShortApproximateEntropy'] = df.Change.rolling(window=short_window, min_periods=1).apply(approx_entropy, raw=True)

	# Spectral Entropy
	df['LongSpectralEntropy'] = df.Change.rolling(window=long_window, min_periods=1).apply(spec_entropy, raw=True)
	df['ShortSpectralEntropy'] = df.Change.rolling(window=short_window, min_periods=1).apply(spec_entropy, raw=True)

	# Autocorrelation
	df['LongAutocorrelation'] = df.Change.rolling(window=long_window, min_periods=1).apply(autocorrelation, raw=False)
	df['ShortAutocorrelation'] = df.Change.rolling(window=short_window, min_periods=1).apply(autocorrelation, raw=False)

	# Stationarity
	df['LongStationarity'] = df.Change.rolling(window=long_window, min_periods=1).apply(stationarity, raw=True)
	df['ShortStationarity'] = df.Change.rolling(window=short_window, min_periods=1).apply(stationarity, raw=True)

	# FILL NA
	df.LongSpectralEntropy.fillna(0, inplace=True)
	df.ShortSpectralEntropy.fillna(0, inplace=True)
	df.LongAutocorrelation.fillna(0, inplace=True)
	df.ShortAutocorrelation.fillna(0, inplace=True)

	# Discard Temp Features
	df.drop(['Volume','VWAP', 'Ticks', 'LongEMA', 'ShortEMA', 'Open', 'High', 'Low', 'Close', 'STDLong', 'STDShort'], axis=1, inplace=True)

	df = df.iloc[long_window:, :]

	## NaN Value Check
	print(df.isnull().sum(axis=0))

	print()

	print(df.head())

	df.to_csv('{}/Features/{}_clean.csv'.format(dir_, ticker), index=False)

######################################################################

def get_tickers():

	tickers = []

	for file in os.listdir(input_dir_):

		ticker = file.split('-')[0]
		tickers.append(ticker) if ticker not in tickers else None

	return tickers

def go_parallel():

	Parallel(n_jobs=n_jobs)(delayed(features)(ticker) for ticker in get_tickers())

def main(ticker):

	if ticker == 'ALL':

		go_parallel()

	else:

		features(ticker)

######################################################################

if __name__ == '__main__':

	argparse = ArgumentParser()
	argparse.add_argument('ticker')
	args = argparse.parse_args()

	main(args.ticker)

