from apscheduler.schedulers.background import BackgroundScheduler

from manager_client import ManagerClient
from mwrapper import mWrapper

from threading import Thread
from datetime import datetime

from zcontracts import forex_contract

##############################

ip_address = '127.0.0.1'
port = 4001
clientId = 1

## TickerDict

ticker_info = {
	"EURUSD" : 0,
	"EURCHF" : 1,
	"EURJPY" : 2
}

order_ints = {
	"BUY" : 1,
	"SELL" : -1
}

order_invs = {
	"BUY" : "SELL",
	"SELL" : "BUY"
}

##############################

class Manager(ManagerClient, mWrapper):

	def __init__(self, ip_address, port):

		mWrapper.__init__(self)
		ManagerClient.__init__(self, self)

		## OrderID
		self.order_id = None

		## Positions Dictionary
		self.trades = {}

		## Reverse Trades Mapping
		self.order_ids = {}

		## Order integers
		self.order_ints = order_ints = {
			"BUY" : 1,
			"SELL" : -1
		}

		## Inverse Orders
		self.order_invs = order_invs = {
			"BUY" : "SELL",
			"SELL" : "BUY"
		}

		## Ticker-reqID mapping
		self.ticker_info = ticker_info = {
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
		self.reqId_info = {ticker_info[key] : key for key in ticker_info.keys()}

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

	def on_close(self):

		self.disconnect()
		self.bg_scheduler.shutdown()

if __name__ == '__main__':

	manager = Manager(ip_address, port)

