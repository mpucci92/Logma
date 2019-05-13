from ibapi.client import EClient
from zcontracts import forex_contract

from datetime import datetime
import time

import pandas as pd
import queue

class ScannerClient(EClient):

	def __init__(self, wrapper):

		EClient.__init__(self, wrapper = wrapper)

	def init_historical_data(self, reqId):

		contract = forex_contract("USD", "JPY")
		gmt_time = datetime.utcnow().strftime('%Y%m%d %H:%M:%S GMT')
		durationStr = "3000 S"
		barSizeSetting = "1 min"
		whatToShow = "MIDPOINT"
		useRTH = 0
		formatDate = 1
		keepUpToDate = True

		dt = datetime.now()
		while dt.second != 0:
			dt = datetime.now()

		self.reqHistoricalData(reqId, contract, '', durationStr,
							   barSizeSetting, whatToShow, useRTH, 
							   formatDate, keepUpToDate, [])

		time.sleep(0.5)

		data = []
		done = False

		while not done:
			try:
				data.append(self.wrapper._historical_queue.get(timeout = 0.1))
			except queue.Empty:
				done = True

		if len(data) < 50:
			print('Error ... initialization not completed')
			self.cancelHistoricalData(reqId)
			time.sleep(1)
			return self.init_historical_data(reqId)

		return data