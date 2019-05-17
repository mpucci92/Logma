from datetime import datetime
from zorders import limit_order, limit_if_touched

class Trade(object):

	def __init__(self, manager, contract, action, initial_order, closing_details):

		## Manager
		self.manager = manager

		## Start Time
		self.init_time = datetime.now()

		## Book keeping
		self.contract = contract
		self.symbol = contract.symbol + contract.currency
		self.action = action
		self.direction = manager.action_directions[action]
		self.closing_action = manager.closing_actions[action]

		## Closing instructions
		self.closing_details = closing_details

		## Trade status
		self.status = 'PENDING'

		## Initial order
		self.init_order = initial_order
		self.init_quantity = initial_order.totalQuantity

		## Keep track of placed orders
		self.placed_orders = []

		## Place initial order
		self.place_order(initial_order)

		## Placeholders
		self.num_filled = 0
		self.remaining = 0

		## Period details
		self.time_period = 1
		self.maturity = 5

	def place_order(self, order):

		oid = self.manager.order_id
		self.manager.placeOrder(oid, self.contract, order)
		
		## Book keeping
		self.manager.orders[oid] = order
		self.manager.order2trade[oid] = self
		self.placed_orders.append((oid, order))

		## Get next ID
		self.manager.reqIds(-1)

	def on_fill(self):

		## Set trade status
		self.status = 'ACTIVE'
		self.execution_time = datetime.now()

		## Send closing orders
		take_profit = self.closing_details['take_profit']
		order = limit_order(action = self.closing_action, quantity = self.init_quantity,
					        price = take_profit, purpose = 'close')
		self.place_order(order)

	def on_close(self):

		## Clean up maps
		for oid, order in self.placed_orders:
			del self.manager.order2trade[oid]
			del self.manager.orders[oid]
			self.manager.cancelOrder(oid)

		# Remove trade from list
		del self.manager.trades[self.symbol]

		## Cancel market data
		self.manager.cancelMktData(self.manager.ticker_ids[self.symbol])

	def on_update(self, price):

		self.last_update = price

		if self.status == 'ACTIVE':

			if self.is_soft_stop():

				target = self.closing_details['soft_stop']
				order = limit_order(action = self.closing_action, quantity = self.init_quantity,
									price = target, purpose = 'close')
				self.place_order(order)
				self.status = 'CLOSING'

			elif self.is_hard_stop():

				hard_stop = self.closing_details['hard_stop']
				order = limit_order(action = self.closing_action, quantity = self.init_quantity,
							        price = hard_stop, purpose = 'close')
				self.place_order(order)
				self.status = 'CLOSING'

		elif self.status == 'PENDING':
			
			if self.is_no_fill():

				self.on_close()

		elif self.status == 'CLOSING':
			pass	

	def is_take_profit(self):
		
		target = self.closing_details['take_profit']
		return self.direction * (self.last_update - target) > 0

	def is_hard_stop(self):

		target = self.closing_details['hard_stop']
		return self.direction * (target - self.last_update) > 0

	def is_soft_stop(self):

		dt = datetime.now()
		target = self.closing_details['soft_stop']
		return dt.minute % 1 == 0 and dt.second == 0 and self.direction * (target - self.last_update) > 0

	def is_matured(self):

		dt = datetime.now()
		delta = dt - self.init_time
		return delta.seconds >= self.time_period * self.maturity * 60

	def is_no_fill(self):

		dt = datetime.now()
		delta = dt - self.init_time
		return self.num_filled == 0 and delta.seconds >= self.time_period * 60

