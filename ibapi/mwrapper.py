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

		if status == 'Filled':
			## Get trade object
			trade = self.order_ids[orderId]
			
			## Set active flag
			trade.is_active = True

			## Store the position filled
			trade.num_filled = filled

			## Take profit
			






	def position(self, account, contract, pos, avgCost):
		pass

	def tickPrice(self, tickerId, field, price, attribs):
		pass


