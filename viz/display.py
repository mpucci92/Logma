import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import mpl_finance as mf
import matplotlib.dates as mdates
import sys, os

def plot_ohlc(data, transactions, q_values, start_idx, period_length):

	data = data[start_idx:start_idx+period_length+5, :].copy()
	colors = ['#AAAAAA', '#77d879']
	data[:, 0] = mdates.date2num(pd.to_datetime(data[:, 0]).values)
	fig, ax = plt.subplots(figsize=(20, 9))

	if len(q_values) == 0:

		for row in data:

		    _ = mf.candlestick_ohlc(ax, [row], width=0.002)

	else:

		for row, qs in zip(data, q_values):
		    
		    amax = np.argmax(qs)
		    color = colors[amax]
		    _ = mf.candlestick_ohlc(ax, [row], width=0.002, 
		                            colorup=color, colordown=color)

	for t in transactions:
	    
	    tag, a, p, prof, idx = t
	    idx -= start_idx+period_length
	    idx += 1
	    color = 'r' if a == -1 else 'g'
	    linestyle = '--' if tag == 'Open Position' else '-'
	    plt.axvline(x=data[idx, 0],
	                linestyle=linestyle,
	                color=color)
	    
	    y_loc = data[:, 4].min()
	    str_ = '%s\nPrice:%.5f$\nProfit:%.2f$' % (tag, p, prof)
	    
	    plt.text(data[idx, 0], y_loc,str_)

	plt.show()

def simple_ohlc(data, idx, save=False, filename=None):

	data = data.copy()
	data[:, 0] = mdates.date2num(pd.to_datetime(data[:, 0]).values)
	fig, ax = plt.subplots(figsize=(20, 9))

	for row in data:

	    _ = mf.candlestick_ohlc(ax, [row], width=0.002)

	plt.axvline(x=data[idx, 0])

	if save:

		plt.savefig(filename)

	else:

		plt.show()

def plot_qs():

	qs = np.load('qs.npy')
	qst = np.load('qst.npy')
	fig, ax = plt.subplots(2, 1, figsize=(30, 8))

	
	ax[0].plot(qs[:, 0], color='grey', label='Neutral')
	ax[0].plot(qs[:, 1], color='green', label='Long')
	ax[0].legend()


	ax[1].plot(qst[:, 0], color='grey', label='Neutral')
	ax[1].plot(qst[:, 1], color='green', label='Long')
	ax[1].legend()
	
	plt.show()

def plot_q_test():

	qst = np.load('qst.npy')
	plt.plot(qst[:, 0], color='grey', label='Neutral')
	plt.plot(qst[:, 1], color='green', label='Long')
	plt.legend()
	plt.show()

def plot_it(env, history, dir_, train=True):

	#### SAVE PLOTS ####
	fig, ax = plt.subplots(6, 1, figsize=(22, 14))
	plt.style.use('bmh')

	ax[0].plot(history.history['episode_reward'], marker='o')
	ax[0].set_title('Rewards')

	ax[1].plot(env.transactions, marker='o')
	ax[1].set_title('Transactions')

	ax[2].plot(env.profits, marker='o')
	ax[2].set_title('Profits')

	ax[3].plot(env.efficiency, marker='o')
	ax[3].set_title('Efficiency')

	ax[4].plot(env.successes, marker='o')
	ax[4].set_title('Success Rate')

	ax[5].plot(env.same_positions, marker='o')
	ax[5].set_title('Same Position')

	#fig.savefig('../plots/dqn_train_{}_batch_size_{}_cutoff_reward.png'.format(batch_size, env.cutoff))
	fig.savefig('{}/plots/plotte_{}.png'.format(dir_, 'train' if train else 'test'))
	plt.close()