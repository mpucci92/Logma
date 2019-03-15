import pandas as pd
import numpy as np
import sys, os
import pickle
from sklearn.preprocessing import StandardScaler
from argparse import ArgumentParser

from consts import dir_

pct = 0.8
n_periods = 20
lower_bound = 0
upper_bound = 10
std_cutoff = 5

def prod(arr):
    relvol = arr[:, -1].reshape(-1, 1)
    X = arr[:, :-1]
    X = np.cumprod(X, axis=1)
    return np.hstack((X, relvol))

def prod_ss(arr, ss):
    relvol = arr[:, -1].reshape(-1, 1)
    X = arr[:, :-1]
    X = np.cumprod(X, axis=1)
    return ss.transform(np.hstack((X, relvol)))

def get_forward_progression(arr, lower, upper):
    p = max(min(np.random.random(), 0.25), 0.75)
    relvol = arr[:, -1:]
    X = arr[:, :-1]
    X = np.cumprod(X, axis=1)
    X = np.hstack((X, relvol))
    return p * X[lower] + (1-p) * X[upper]

def logscale_outliers(arr, std_cutoff):
    arr[arr > (1+std_cutoff)] = np.log10(arr[arr > (std_cutoff+1)] - std_cutoff)+std_cutoff
    arr[arr < -(1+std_cutoff)] = -1*(np.log10(-1*arr[arr < -(std_cutoff+1)]-std_cutoff)+std_cutoff)
    return arr

def data_prep(ticker):

	print('Load Data')
	df = pd.read_csv('{}/{}_clean.csv'.format(dir_, ticker))
	dates = df.Datetime.values
	df = df.iloc[:, 2:]
	print(df.head())
	print()
	df = df[['Open', 'High', 'Low', 'Close', 'Dist10MA', 'Dist20MA', 'Dist50MA','Dist200MA', 'CBSpread', 'BB', 'RelVol']]

	idc = int(len(df)*pct)
	test = df.values[idc:]
	train = df.values[:idc]

	print('y_train')
	ss_train = StandardScaler()
	y_train = np.array([get_forward_progression(train[i:i+upper_bound], lower_bound, upper_bound-1) for i in range(n_periods, len(train)-upper_bound)])
	ss_train = ss_train.fit(y_train)
	y_train = ss_train.transform(y_train)

	print('X_train')
	X_train = np.array([prod(train[i-n_periods:i]) for i in range(n_periods, len(train))])
	x_ss = X_train.reshape(X_train.shape[0]*X_train.shape[1], -1)
	ss_prog = StandardScaler().fit(x_ss)

	X_train = [prod_ss(train[i-n_periods:i], ss_prog) for i in range(n_periods, len(train))]
	X_train = np.array(X_train)
	X_train = X_train[:-upper_bound, :]

	print('X_y_val')
	X_val = np.array([prod_ss(test[i-n_periods:i], ss_prog) for i in range(n_periods, len(test))])
	y_val = ss_train.transform([get_forward_progression(test[i:i+upper_bound], 0, upper_bound-1) for i in range(n_periods, len(test)-upper_bound)])
	X_val = X_val[:-upper_bound, :]

	print('Shuffle')
	idc = np.random.permutation(X_train.shape[0])
	X_train = X_train[idc]
	y_train = y_train[idc]

	idc = np.random.permutation(X_val.shape[0])
	X_val = X_val[idc]
	y_val = y_val[idc]

	print('Logscale')
	X_train = logscale_outliers(X_train, std_cutoff)
	y_train = logscale_outliers(y_train, std_cutoff)
	X_val = logscale_outliers(X_val, std_cutoff)
	y_val = logscale_outliers(y_val, std_cutoff)

	print('Saving Arrays')
	for arr, filename in zip([X_train, y_train, X_val, y_val], ['X_train.npy', 'y_train.npy', 
																'X_val.npy', 'y_val.npy']):
		np.save('{}/{}'.format(dir_, '{}_{}'.format(ticker, filename)), arr)

	print('Saving X_new')
	X_new = np.save('{}/{}_X_new.npy'.format(dir_, ticker), np.array([prod_ss(df.values[i-n_periods:i].copy(), ss_prog) for i in range(n_periods, df.values.shape[0])]))
	dates = np.save('{}/{}_dates.npy'.format(dir_, ticker), dates[n_periods:])
	print('Done')

def load_data(ticker):
	filenames = ['X_train.npy', 'y_train.npy', 'X_val.npy', 'y_val.npy']
	filenames = ['{}_{}'.format(ticker, filename) for filename in filenames]
	return (np.load('{}/{}'.format(dir_, filename)) for filename in filenames)

def get_X_new(ticker):

	return (np.load('{}/{}_X_new.npy'.format(dir_, ticker)), np.load('{}/{}_dates.npy'.format(dir_, ticker)))

if __name__ == '__main__':

	argparser = ArgumentParser()
	argparser.add_argument('ticker')
	args = argparser.parse_args()

	data_prep(args.ticker)
