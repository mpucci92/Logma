from scanner.scanner import Scanner
from manager.manager import Manager

from zmodel import Model

class Strategy(object):

	ip_address = '192.168.2.26'
	port = 4001

	def __init__(self, num_periods, time_period):

		## Client IDs
		self.client2id = {
			"scanner" : 0,
			"manager" : 1
		}

		## Ticker-reqID mapping
		self.ticker2id = {
			"EURCHF" : 0,
			"USDCHF" : 1,
			"GBPUSD" : 2,
			"USDJPY" : 3,
			"EURUSD" : 4,
			"EURGBP" : 5,
			"NZDUSD" : 6,
			"USDCAD" : 7,
			"EURJPY" : 8,
			"AUDUSD" : 9,
			"GBPJPY" : 10,
			"CHFJPY" : 11,
			"AUDNZD" : 12,
			"CADJPY" : 13
		}

		## Reverse mapping
		self.id2ticker = {self.ticker2id[key] : key for key in self.ticker2id.keys()}

		## Contracts
		self.contracts = {key : forex_contract(key[:3], key[3:]) for key in self.ticker2id}

		## Tick Increments
		self.tick_increments = {
			"EURCHF" : 0.00005,
			"USDCHF" : 0.00005,
			"GBPUSD" : 0.00005,
			"USDJPY" : 0.005,
			"EURUSD" : 0.00005,
			"EURGBP" : 0.00005,
			"NZDUSD" : 0.00005,
			"USDCAD" : 0.00005,
			"EURJPY" : 0.005,
			"AUDUSD" : 0.00005,
			"GBPJPY" : 0.005,
			"CHFJPY" : 0.005,
			"AUDNZD" : 0.00005,
			"CADJPY" : 0.005
		}

		## Strategy configuration
		self.num_periods = num_periods
		self.time_period = time_period

		## Scanner for finding signals
		self.scanner = Scanner(ip_address = self.ip_address, port = self.port, clientId = self.client2id['scanner'],
							   ticker2id = self.ticker2id, id2ticker = self.id2ticker, contracts = self.contracts,
							   tick_increments = self.tick_increments)

		## Manager for managing trades
		self.manager = Manager(ip_address = self.ip_address, port = self.port, clientId = self.client2id['manager'],
							   ticker2id = self.ticker2id, id2ticker = self.id2ticker, contracts = self.contracts,
							   tick_increments = self.tick_increments)

	def on_start(self):

		self.scanner.on_start()
		self.manager.on_start()

	def on_close(self):

		self.scanner.on_close()
		self.manager.on_close()


