from apscheduler.schedulers.background import BackgroundScheduler
import joblib

from scanner_wrapper import ScannerWrapper
from scanner_client import ScannerClient

from datetime import datetime, timedelta
from collections import namedtuple
from threading import Thread
import queue, time

## Might not need
from zmodel import Model
from zcontracts import forex_contract

##############################

ip_address = '127.0.0.1'
port = 4001
clientId = 0

DataConfig = namedtuple('DataConfig', ['durationStr', 'barSizeSetting', 'whatToShow',
									   'useRTH', 'formatDate', 'keepUpToDate'])

##############################

class Scanner(ScannerClient, zWrapper):

	def __init__(self, ip_address, port, clientId, ticker2id, id2ticker, contracts, tick_incremenets, num_periods, time_period):

		zWrapper.__init__(self)
		ScannerClient.__init__(self, self)

		## Instrument configuration
		self.ticker2id = ticker2id
		self.id2ticker = id2ticker
		self.contracts = contracts
		self.tick_incremenets = tick_incremenets

		## Strategy configuration
		self.num_periods = num_periods
		self.time_period = time_period

		## Data storages
		self.storages = {}

		## Historical data configuration
		self.config = DataConfig(
				durationStr = "{} S".format(time_period * num_periods),
				barSizeSetting = "{} min".format(time_period),
				whatToShow = "MIDPOINT",
				useRTH = 0,
				formatDate = 1,
				keepUpToDate = True
			)

		self.init_errors()

		self.connect(ip_address, port, clientId)

		thread = Thread(target = self.run)
		thread.start()

		self.print_errors()

	def on_start(self, reqId):

		## Initialize Storages for each ticker
		self.init_historical_data()

	def on_close(self):

		self.disconnect()

if __name__ == '__main__':

	scanner = Scanner(ip_address, port, clientId)