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
		self.logger.warning('Next order ID {}'.format(orderId))
		self.order_id = orderId

	def orderStatus(self, orderId, status, filled, remaining, avgFilledPrice, 
					permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):

		try:

			## Get the trade object this order is concerning
			trade = self.order_ids[orderId]

			## Get the order itself
			order = self.orders[orderId]

			self.logger.warning('\nOrder Status {} for ticker {} - {}. Purpose: '.format(status, trade.symbol, orderId, order.purpose))

			if order.purpose == 'initiate':

				self.logger.warning('Order status update for an initiator')

				## Store the position filled
				trade.num_filled = filled

				## Store the remaining to be filled
				trade.num_remaining = remaining

				## Store the average cost of the position
				trade.avg_fill_price = avgFilledPrice

				if status == 'Filled':

					self.logger.warning('\nTrade {} was filled for ticker {} at avg price {}'.format(orderId, trade.symbol, avgFilledPrice))

					trade.on_fill()

			elif order.purpose == 'close':

				## Store position filled on close
				trade.num_filled_on_close = filled

				## Increment the number of remaining
				trade.num_remaining_on_close = remaining

				if status == 'Filled':

					self.logger.warning('\nClosing Trade {} was filled for ticker {} at avg price {}'.format(orderId, trade.symbol, avgFilledPrice))
					self.logger.warning('Num Filled on Initiate {} same as Num Filled on Close {}'.format(trade.num_filled, trade.num_filled_on_close))

					## Clean up maps
					for id_ in trade.executed_ids:
						del self.order_ids[id_]
						del self.orders[id_]
					del self.trades[trade.symbol]

					## Cancel market data
					self.cancelMktData(self.ticker_ids[trade.symbol])

		except Exception as e:
			print(e)

	def position(self, account, contract, pos, avgCost):
		
		self.logger.warning('\nPosition Change for {}, total {} quantity at {} cost'.format(contract.symbol+contract.curreny, pos, avgCost))

	def tickPrice(self, tickerId, field, price, attribs):

		trade = self.trades[self.id_tickers[tickerId]]

		if field == self.tick_types[trade.direction]:
			
			trade.on_update(price, self.logger, self)

	def marketDataType(self, reqId, marketDataType):

		print('\n\nReqId', reqId, 'Data Type', marketDataType)
