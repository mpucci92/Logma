import numpy as np
import pandas as pd
import sys, os
import seaborn as sns
from IPython.display import clear_output
from sklearn.preprocessing import StandardScaler

from consts import dir_

window = 20
cutoff = 100

def long_short_ttc(datetime, df, opens, highs, lows, closes):
    
    idx = df[df.Datetime == datetime].index.values[0]
    target = opens[idx]
    close, low = np.inf, np.inf
    
    ctr = idx
    while close > target and low > target:
        idx += 1
        close = closes[idx]
        low = lows[idx]
        if idx - ctr >= cutoff:
            break
    return idx - ctr

def short_long_ttc(datetime, df, opens, highs, lows, closes):
    
    idx = df[df.Datetime == datetime].index.values[0]
    target = opens[idx]
    close, high = -np.inf, -np.inf
    
    ctr = idx
    while close < target and high < target:
        idx += 1
        close = closes[idx]
        high = highs[idx]
        if idx - ctr >= cutoff:
            break
    return idx - ctr

def get_signals(raw):

	raw['Change'] = (raw.Close - raw.Open) / raw.Open
	df = raw

	df['STD'] = df.Change.rolling(window=window, min_periods=1).std()
	df['Mean'] = df.Change.rolling(window=window, min_periods=1).mean()

	cutoff = 3
	longs = df[df.Change > cutoff*df.STD + df.Mean]
	longs = longs[longs.STD != 0]
	shorts = df[df.Change < df.Mean - cutoff*df.STD]
	shorts = shorts[shorts.STD != 0]

	print('Num Longs', longs.shape[0])
	print('Num Shorts', shorts.shape[0])

	ttc_long = []
	print('TTC Longs')
	opens = df.Open.values
	highs = df.High.values
	lows = df.Low.values
	closes = df.Close.values
	for i, datetime in enumerate(longs.Datetime):
	    print(i)
	    ttc_long.append(long_short_ttc(datetime, df, opens, highs, lows, closes))

	ttc_longs = pd.DataFrame(ttc_long, columns=['TTC'])
	ttc_longs['Datetime'] = longs.Datetime.values
	print(ttc_longs.describe())

	ttc_short = []
	print('TTC Shorts')
	for i, datetime in enumerate(shorts.Datetime):
	    print(i)
	    ttc_short.append(short_long_ttc(datetime, df, opens, highs, lows, closes))

	ttc_shorts = pd.DataFrame(ttc_short, columns=['TTC'])
	ttc_shorts['Datetime'] = shorts.Datetime.values
	print(ttc_shorts.describe())

	ttc_longs.to_pickle('{}/shorts.pkl'.format(dir_))
	ttc_shorts.to_pickle('{}/longs.pkl'.format(dir_))

if __name__ == '__main__':

	raw = pd.read_csv('D:/TickData_Agg/EURUSD_new.csv')

	sys.exit(get_signals(raw))