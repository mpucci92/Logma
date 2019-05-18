from apscheduler.schedulers.background import BackgroundScheduler

from manager_client import ManagerClient
from mwrapper import mWrapper

from threading import Thread
from datetime import datetime

from zcontracts import forex_contract

import logging

##############################

ip_address = '192.168.2.26'
port = 4001
clientId = 1

##############################

class Manager(ManagerClient, mWrapper):

	def __init__(self, ip_address, port):

		mWrapper.__init__(self)
		ManagerClient.__init__(self, self)

		## Reserve OrderIDs
		self.order_id_offset = 0

		## OrderID
		self.order2trade = {}

		## Symbol to Trade object mapping
		self.trades = {}

		## OrderId to Order mapping
		self.orders = {}

		## Reverse OrderID-Trade Mapping
		self.order_ids = {}

		## Direction integer mappings
		self.action_directions = {
			"BUY" : 1,
			"SELL" : -1
		}

		## Direction tick types
		self.tick_types = {
			1 : 1,
			-1 : 2
		}

		## Inverse Orders
		self.closing_actions = {
			"BUY" : "SELL",
			"SELL" : "BUY"
		}

		## Ticker-reqID mapping
		self.ticker_ids = {
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
		self.id2ticker = {self.ticker_ids[key] : key for key in self.ticker_ids.keys()}

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

		## Contracts
		self.contracts = {key : forex_contract(key[:3], key[3:]) for key in self.ticker_ids}

		## Errors
		self.init_errors() 

		## Scheduler
		self.bg_scheduler = BackgroundScheduler()

		## Connect to gateway
		self.connect(ip_address, port, 1)

		## Init message loop
		thread = Thread(target = self.run)
		thread.start()

		## Errors
		self.wrapper.print_errors()

	def now(self):

		return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	def on_close(self):

		## Close all orders
		self.reqGlobalCancel()

		self.disconnect()
		self.bg_scheduler.shutdown()

if __name__ == '__main__':

	manager = Manager(ip_address, port)

