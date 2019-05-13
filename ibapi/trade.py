from datetime import datetime

class Trade(object):

	def __init__(self, contract, direction, order, orderId,
				 tp_order, ss_order, hs_order, tp_orderId = None,
				 ss_orderId = None, hs_orderId = None):

		self.num_filled = None
		self.num_remaining = None

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
		self.isActive = False

	def on_update(self):

		if self.isActive:

			if self.is_take_profit():

				return 'Execute', self.take_profit['Order']

			elif self.is_soft_stop():

				return 'Execute', self.soft_stop['Order']

			elif self.is_hard_stop():

				return 'Execute', self.hard_stop['Order']
		
		else:

			dt = datetime.now() - self.init_time

			if dt.seconds >= 5 * 60 and self.num_filled == 0:
				
				return 'Cancel', self.init_order_id

			elif dt.seconds >= 5 * 60 and self.num_filled != 0:

				## Adjust take profit
				self.take_profit['Order'].quantity = num_filled

				## Adjust soft stop
				self.soft_stop['Order'].quantity = num_filled

				## Adjust hard stop
				self.hard_stop['Order'].quantity = num_filled

				## Set as active trade
				self.is_active = True

				return 'Partial', self.init_order_id

	def on_fill(self):

		## Set active flag
		self.isActive = True
		self.execution_time = datetime.now()

	def is_take_profit(self):
		
		return self.direction * (self.latest_update - self.take_profit['Price']) > 0

	def is_soft_stop(self):

		dt = datetime.now()
		return dt.minute % 5 == 0 and dt.second == 0 and self.direction * (self.soft_stop['Price'] - self.latest_update) > 0		

	def is_hard_stop(self):
		
		return self.direction * (self.hard_stop['Price'] - self.latest_update) > 0