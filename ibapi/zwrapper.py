from ibapi.wrapper import EWrapper

import queue

import numpy as np
import pandas as pd
from datetime import datetime

class zWrapper(EWrapper):

	def init_errors(self):
		self._errors = queue.Queue()

	def is_error(self):
		return not self._errors.empty()

	def get_error(self, timeout):
		if self.is_error():
			try:
				return self._errors.get(timeout = timeout)
			except queue.Empty:
				return 'Timeout'

	def error(self, id_, error_code, error_msg):
		msg = '{}/{} ... {}'.format(id_, error_code, error_msg)
		self._errors.put(msg)

	def print_errors(self):
		while self.is_error():
			print(self.get_error(0.1))

	def init_historical_queue(self):
		self._historical_queue = queue.Queue()

	def init_updates_queue(self):
		self._updates_queue = queue.LifoQueue()

	def historicalData(self, reqId, bar):
		self._historical_queue.put((bar.date, bar.open, bar.high, bar.low, bar.close))

	def historicalDataUpdate(self, reqId, bar):
		self._updates_queue.put((bar.date, bar.open, bar.high, bar.low, bar.close))

	def historicalDataEnd(self, reqId, start, end):
		print('Start', start, 'End', end)

