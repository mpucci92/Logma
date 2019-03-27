import pandas as pd
import numpy as np
import sys, os
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser

from consts import dir_

#Rel Vol 1-week MA
n_periods = 7
n_candles = 480

#Long/Short windows
short_window = 20
long_window = 50

def filter_weekends(df):
    df['Datetime'] = pd.to_datetime(df.Datetime)
    df['DayName'] = df.Datetime.dt.weekday_name
    df = df[~df.DayName.isin(['Saturday', 'Sunday'])]
    return df.drop('DayName', axis=1)

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

def features(ticker):

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

	df['LongKurtosis'] = df.Change.rolling(window=long_window, min_periods=1).kurt()
	df['ShortKurtosis'] = df.Change.rolling(window=short_window, min_periods=1).kurt()

	#Volume Indicatorss
	df['Ticks'] = np.log(df.Ticks)

	#Positioning Indicators
	df['LongEMA'] = df.Close.ewm(span=long_window, min_periods=1).mean()
	df['ShortEMA'] = df.Close.ewm(span=short_window, min_periods=1).mean()

	df['DLongEMA'] = df.Close / df['LongEMA'].values
	df['DShortEMA'] = df.Close / df['ShortEMA'].values

	### Center Metrics Around 1
	for col in df.columns:
	    if col in ['Open', 'High', 'Low', 'Close', 'VWAP']:
	        df[col] = df[col].pct_change() + 1

	def cp(x):
		return x.cumprod()[-1]

	## Relative Volume
	df = compute_relative_volume(df, n_periods, n_candles)

	# Fill Missing Values
	df['VWAP'] = df.VWAP.fillna(value=1)
	df['VWAP'] = df.VWAP.replace(to_replace=np.inf, value=1)

	df['LongSkew'] = df.LongSkew.fillna(value=0)
	df['ShortSkew'] = df.ShortSkew.fillna(value=0)

	df['LongKurtosis'] = df.LongKurtosis.fillna(value=0)
	df['ShortKurtosis'] = df.ShortKurtosis.fillna(value=0)
	
	df['Ticks'] = df.Ticks.replace(to_replace=-np.inf, value=0)

	df['RelVol'] = df.RelVol.replace(to_replace=np.nan, value=0)

	# Time series progressions
	df['LongProg'] = df.Close.rolling(window=long_window, min_periods=1).apply(cp)
	df['LongVProg'] = df.VWAP.rolling(window=long_window, min_periods=1).apply(cp)

	df['ShortProg'] = df.Close.rolling(window=short_window, min_periods=1).apply(cp)
	df['ShortVProg'] = df.VWAP.rolling(window=short_window, min_periods=1).apply(cp)

	# Discard Temp Features
	df.drop(['Volume','VWAP', 'LongEMA', 'ShortEMA', 'Open', 'High', 'Low', 'Close', 'STDLong', 'STDShort'], axis=1, inplace=True)

	## NaN Value Check
	print(df.isnull().sum(axis=0))

	print()

	print(df.head())

	df.to_csv('{}/{}_clean.csv'.format(dir_, ticker), index=False)

if __name__ == '__main__':

	argparse = ArgumentParser()
	argparse.add_argument('ticker')
	args = argparse.parse_args()

	features(args.ticker)

