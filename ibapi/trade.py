from datetime import datetime

class Trade(object):

	def __init__(self, contract, direction, order, orderId,
				 tp_order, ss_order, hs_order, tp_orderId = None,
				 ss_orderId = None, hs_orderId = None):

		self.num_filled = None
		self.num_remaining = None

		self.executed_ids = [orderId]

		self.on_signal(contract, direction, order, orderId)

		self.take_profit = {
			"Price" : tp_order.lmtPrice,
			"Order" : tp_order,
			"OrderId" : tp_orderId
		}
		self.soft_stop = {
			"Price" : ss_order.lmtPrice,
			"Order" : ss_order,
			"OrderId" : ss_orderId
		}
		self.hard_stop = {
			"Price" : hs_order.lmtPrice,
			"Order" : hs_order,
			"OrderId" : hs_orderId
		}

	def on_signal(self, contract, direction, order, orderId):

		self.init_time = datetime.now()
		self.contract = contract
		self.symbol = contract.symbol + contract.currency
		self.direction = direction
		self.init_order = order
		self.init_order_id = orderId
		self.is_active = False

	def on_update(self, price, logger, manager):

		self.latest_update = price
		self.logger = logger
		self.logger.warning('{} -- Price : {}'.format(self.symbol, price))

		order = None

		if self.is_active:

			self.logger.warning('\nTrade is active')

			if self.is_take_profit():

				self.logger.warning('Taking Profit')
				order = self.take_profit['Order']

			elif self.is_soft_stop():

				self.logger.warning('Soft Stop')
				order = self.soft_stop['Order']

			elif self.is_hard_stop():

				self.logger.warning('Hard Stop')
				order = self.hard_stop['Order']

			if order is not None:

				manager.placeOrder(manager.order_id, self.contract, order)

				manager.order_ids[manager.order_id] = self
				manager.orders[manager.order_id] = order

				self.executed_ids.append(manager.order_id)

				manager.reqIds(-1)

				self.is_active = False

	def on_fill(self):

		## Set active flag
		self.is_active = True
		self.execution_time = datetime.now()

	def is_take_profit(self):
		
		self.logger.warning('Take Profit {}'.format(self.direction * (self.latest_update - self.take_profit['Price'])))
		return self.direction * (self.latest_update - self.take_profit['Price']) > 0

	def is_soft_stop(self):

		dt = datetime.now()
		self.logger.warning('Soft Stop {}'.format(self.direction * (self.soft_stop['Price'] - self.latest_update)))
		return dt.minute % 1 == 0 and dt.second == 0 and self.direction * (self.soft_stop['Price'] - self.latest_update) > 0		

	def is_hard_stop(self):
		
		self.logger.warning('Hard Stop {}'.format(self.direction * (self.hard_stop['Price'] - self.latest_update)))
		return self.direction * (self.hard_stop['Price'] - self.latest_update) > 0