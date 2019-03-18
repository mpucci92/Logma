import data_prep as dp
import pandas as pd
import data_transform as dt
import train_nn as tnn
from argparse import ArgumentParser

from consts import dir_
import time

def time_it(start, label):
	print('%s %.3f Minutes' % (label, (time.time() - start)/60))
	return time.time()

if __name__ == '__main__':

	argparser = ArgumentParser()
	argparser.add_argument('file')
	argparser.add_argument('ticker')
	argparse = argparser.parse_args()

	print('Pipeline Start')

	start_total = time.time()
	start = start_total
	dt.features(argparse.file, argparse.ticker)
	start = time_it(start, 'Feature Engineering')

	dp.data_prep(argparse.ticker)
	start = time_it(start, 'Data Transforming')

	tnn.main(argparse.ticker)
	start = time_it(start, 'Time Series Embedding')

	raw = pd.read_csv(argparse.file)
	embeds = pd.read_pickle('{}/{}_embed.pkl'.format(dir_, argparse.ticker))
	raw['Datetime'] = pd.to_datetime(raw.Datetime)
	embeds['Datetime'] = pd.to_datetime(embeds.Datetime)
	final = embeds.merge(raw, how='outer', on='Datetime').dropna().set_index('Datetime')
	final.to_pickle('{}/{}_rl.pkl'.format(dir_, argparse.ticker))
	time_it(start, 'RL Data Aggregation')

	print('Done', '%.3f Minutes' % ((time.time() - start_total)/60))