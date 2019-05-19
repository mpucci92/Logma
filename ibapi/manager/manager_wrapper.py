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
		self.order_id = orderId + self.order_id_offset

	def orderStatus(self, orderId, status, filled, remaining, avgFilledPrice, 
					permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):

		try:

			## Get the trade object this order is concerning
			trade = self.order2trade[orderId]

			## Get the order itself
			order = self.orders[orderId]

			if order.purpose == 'initiate':

				## Store the position filled
				trade.num_filled = filled

				## Store the average cost of the position
				trade.avg_fill_price = avgFilledPrice

				if status == 'Filled':

					trade.on_fill()

			elif order.purpose == 'close':

				## Store position filled on close
				trade.num_filled_on_close = filled

				if status == 'Filled':

					## Close the trade
					trade.on_close()

		except Exception as e:
			print(e)

	def tickPrice(self, tickerId, field, price, attribs):

		trade = self.trades[self.id2ticker[tickerId]]
		if field == self.tick_types[trade.direction]:
			trade.last_update = price

	def marketDataType(self, reqId, marketDataType):

		print('\n\nReqId', reqId, 'Data Type', marketDataType)
