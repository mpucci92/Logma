import numpy as np
import pandas as pd

import sys, os

input_dir_ = 'D:/TickData_UZ/'

def get_tickers():

	tickers = []
	for file in os.listdir(input_dir_):
		ticker = file.split('-')[0]
		tickers.append(ticker) if ticker not in tickers else None
	return tickers

def main():

	tickers = get_tickers()

	for ticker in tickers:

		raw = pd.read_csv('D:/TickData_Agg/{}.csv'.format(ticker))
		features = pd.read_csv('D:/AlgoMLData/Features/{}_clean.csv'.format(ticker))

		raw['DLongSMA'] = raw.Close / raw.Close.rolling(window=50, min_periods=1).mean()
		raw['DShortSMA'] = raw.Close / raw.Close.rolling(window=20, min_periods=1).mean()

		features_new = features.merge(raw[['Datetime', 'DLongSMA', 'DShortSMA']], how='outer', on='Datetime').dropna()
		cols = ' '.join(features.columns.tolist())
		cols = cols.replace('DLongEMA', 'DLongSMA').replace('DShortEMA', 'DShortSMA')
		features_new = features_new[cols.split()]

		features_new.to_csv('D:/AlgoMLData/Features_new/{}_clean.csv'.format(ticker), index=False)

if __name__ == '__main__':

	main()