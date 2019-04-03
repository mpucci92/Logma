import pandas as pd
import numpy as np
import sys, os

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from argparse import ArgumentParser
from joblib import Parallel, delayed

from consts import dir_

upper = 0.99
lower = 0.01

n_jobs = 6

input_dir_ = 'D:/TickData_UZ'.format(dir_)

def log_trimming(x, cutoff_gt, cutoff_lt):

	x = x.copy()
	x[x > cutoff_gt] = cutoff_gt + np.log(x[x > cutoff_gt] - cutoff_gt + 1)
	x[x < cutoff_lt] = cutoff_lt - np.log(abs(x[x < cutoff_lt]) - abs(cutoff_lt) + 1)
	return x

def iqr_trimming(x, upper, lower):

	iqr = np.quantile(x, upper) - np.quantile(x, lower)
	upper_fence = np.quantile(x, upper) + 1.5*iqr
	lower_fence = np.quantile(x, lower) - 1.5*iqr

	x[x > upper_fence] = upper_fence + x[x > upper_fence]/100
	x[x < lower_fence] = lower_fence - x[x < lower_fence]/100

	return x

def scale_it(ticker):

	print(ticker)

	features = pd.read_csv('{}/Features/{}_clean.csv'.format(dir_, ticker))
	trades =  pd.read_csv('{}/Trades/{}_trades.csv'.format(dir_, ticker))

	features.LongKurtosis = log_trimming(features.LongKurtosis.values.copy(), 10, -10)
	features.ShortKurtosis = log_trimming(features.ShortKurtosis.values.copy(), 10, -10)

	x = features.Change.values.copy()
	features.Change = iqr_trimming(x, upper, lower)

	x = features.DLongEMA.values.copy()
	features.DLongEMA = iqr_trimming(x, upper, lower)

	x = features.DShortEMA.values.copy()
	features.DShortEMA = iqr_trimming(x, upper, lower)

	x = features.LongProg.values.copy()
	features.LongProg = iqr_trimming(x, upper, lower)

	x = features.ShortProg.values.copy()
	features.ShortProg = iqr_trimming(x, upper, lower)

	### SCALING
	drop = ['ShortSpectralEntropy']
	no_scale = ['LongStationarity', 'ShortStationarity']

	ss = StandardScaler()

	X_scale = features[[col for col in features.columns if col not in drop+no_scale+['Datetime']]]
	X_train = X_scale.iloc[:int(X_scale.shape[0]*0.9), :]
	ss = ss.fit(X_train)
	X_scale = ss.transform(X_scale)

	features.loc[:, [col for col in features.columns if col not in drop+no_scale+['Datetime']]] = X_scale

	features['Change'] = log_trimming(features.Change.values.copy(), 7, -7)
	features['LongProg'] = log_trimming(features.LongProg.values.copy(), 7, -7)
	features['ShortProg'] = log_trimming(features.ShortProg.values.copy(), 7, -7)
	features['DLongEMA'] = log_trimming(features.DLongEMA.values.copy(), 7, -7)
	features['DShortEMA'] = log_trimming(features.DShortEMA.values.copy(), 7, -7)

	trades = trades.merge(features, on='Datetime', how='outer').dropna().drop('ShortSpectralEntropy', axis=1)

	print()

	print(trades[['LongKurtosis', 'ShortKurtosis', 'LongProg', 'ShortProg', 'DShortEMA']].describe())

	print()

	trades.to_csv('{}/Scaled/{}_scaled.csv'.format(dir_, ticker))

def get_tickers():

	tickers = []

	for file in os.listdir(input_dir_):

		ticker = file.split('-')[0]
		tickers.append(ticker) if ticker not in tickers else None
	print(tickers)
	return tickers

def go_parallel():

	Parallel(n_jobs=n_jobs)(delayed(scale_it)(ticker) for ticker in get_tickers())

def main(ticker):

	if ticker == 'ALL':

		go_parallel()

	else:

		scale_it(ticker)

if __name__ == '__main__':

	argparse = ArgumentParser()
	argparse.add_argument('ticker')
	args = argparse.parse_args()

	main(args.ticker)
