import pandas as pd
import sys, os
import numpy as np

main = []
ticker = 'EURUSD'
dir_ = 'D:\\TickData_UZ\\'
min_ = 3

def vwap(data):
    x = data.value_counts(sort=False).reset_index().values
    p, q = x[:, 0], x[:, 1]
    return (p * (q / q.sum())).sum()

for file in os.listdir(dir_):

	if file.split('-')[0] == ticker:
		
		print(file)
		df = pd.read_csv(dir_+file, header=None, names=['Ticker', 'Datetime', 'Bid', 'Ask'])
		df['Datetime'] = pd.to_datetime(df.Datetime)
		df.set_index('Datetime', inplace=True)
		df['Price'] = (df['Bid'] + df['Ask'])/2

		df = df.resample('%dT' % min_).agg({
		    'Price' : [('Open', 'first'),  
		               ('High', 'max'),
		               ('Low', 'min'),
		               ('Close', 'last'), 
		               ('Volume', 'sum'),
		               ('Ticks', 'count'), 
		               ('VWAP', vwap)]
		})
		df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Ticks', 'VWAP']
		print(df.head())
		
		for col in df.columns:
			t = df[col]
			if col != 'Volume':
			    t = t.fillna(method='backfill')
			    df[col] = t.values
			else:
			    t = t.fillna(value=0)
			    df[col] = t.values

		main.append(df)
	
main = pd.concat(main, axis=0)

main.to_csv('D:\\TickData_Agg\\'+ticker+'_new.csv')
