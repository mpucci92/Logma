import pandas as pd
import numpy as np
import sys, os
import matplotlib.pyplot as plt
import seaborn as sns
from argparse import ArgumentParser

from consts import dir_

n_periods = 60
n_candles = 480
window = 20

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

def features(file, ticker):

	df = pd.read_csv(file)
	df = filter_weekends(df)

	df['Change'] = (df.Close - df.Open) / df.Open
	## Distribution Statistics
	df['STD'] = df.Change.rolling(window=window, min_periods=1).std()
	df['Vol'] = df.STD/np.sqrt(window)
	df['Skew'] = df.Change.rolling(window=window, min_periods=1).skew()
	# Excess Kurtosis
	df['Kurtosis'] = df.Change.rolling(window=window, min_periods=1).kurt()-3
	df['Ticks'] = np.log(df.Ticks)

	### Center Metrics Around 1
	for col in df.columns:
	    if col in ['Open', 'High', 'Low', 'Close']:
	        df[col] = df[col].pct_change() + 1

	## Discard Temp Features
	df.drop(['STD'], axis=1, inplace=True)

	## Relative Volume
	df = compute_relative_volume(df, n_periods, n_candles)
	df.drop('Volume', axis=1, inplace=True)

	## NaN Value Check
	print(df.isnull().sum(axis=0))

	df.to_csv('{}/{}_clean.csv'.format(dir_, ticker))

if __name__ == '__main__':

	argparse = ArgumentParser()
	argparse.add_argument('file')
	argparse.add_argument('ticker')
	args = argparse.parse_args()

	features(args.file, args.ticker)

