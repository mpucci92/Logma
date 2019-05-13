from ibapi.wrapper import EWrapper

import numpy as np

import sys, os
import queue
from queue import Queue, LifoQueue

class mWrapper(EWrapper):

	def init_errors(self):
		self._errors = Queue()

	def is_error(self):
		return not self._errors.empty()

	def get_error(self, timeout = 0.1):
		if self.is_error():
			try:
				return self._errors.get(timeout = timeout)
			except queue.Empty:
				return 'Timeout'

	def print_errors(self, timeout = 0.1):
		while self.is_error():
			print(self.get_error(timeout = timeout))

	def error(self, id_, error_code, error_msg):
		msg = '{}/{} ... {}'.format(id_, error_code, error_msg)
		self._errors.put(msg)

	def nextValidId(self, orderId):
		print('OID', orderId)
		self.order_id = orderId

	def orderStatus(self, orderId, status, filled, remaining, avgFilledPrice, 
					permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):

		trade = self.order_ids[orderId]

		print('\n\nOrder Status {} for ticker {}'.format(status, trade.symbol))

		## Store the position filled
		trade.num_filled = filled

		## Store the remaining to be filled
		trade.num_remaining = remaining

		## Store the average cost of the position
		trade.avg_fill_price = avgFilledPrice

		if status == 'Filled':

			print('\n\nTrade {} was filled for ticker {} at avg price {}'.format(orderId, trade.symbol, avgFilledPrice))

			trade.is_active = True

	def position(self, account, contract, pos, avgCost):
		
		print('\n\nPosition Change for {}, total {} quantity at {} cost'.format(contract.symbol+contract.curreny, pos, avgCost))

	def tickPrice(self, tickerId, field, price, attribs):

		trade = self.trades[self.id_tickers[tickerId]]
		if field == self.tick_types[trade.direction]:
			trade.latest_update = price

	def marketDataType(self, reqId, marketDataType):

		print('\n\nReqId', reqId, 'Data Type', marketDataType)
