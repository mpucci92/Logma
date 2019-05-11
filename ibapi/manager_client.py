from ibapi.client import EClient
from ibapi.order import Order

from zcontracts import forex_contract
from zorders import market_order

import queue

import time

class Trade(Object):

	def __init__(self, contract, direction, order):

		self.on_signal(contract, direction, order)

		self.execution_time = None
		self.take_profit = None
		self.soft_stop = None
		self.hard_stop = None

	def on_signal(self, contract, direction, order):

		self.init_time = datetime.now()
		self.contract = contract
		self.symbol = contract.symbol + contract.currency
		self.direction = direction
		self.init_order = order
		self.isActive = False

	def on_update(self):

		## Check if need to execute any of the orders

class ManagerClient(EClient):

	def __init__(self, wrapper):

		EClient.__init__(self, wrapper = wrapper)
		self.position_dict = {}

	def at_price(self, direction, price, action, quantity, t1, t2):

		direction_int = 1 if direction == "BUY" else -1

		## Symbol
		symbol = t1+t2

		## Contract
		contract = forex_contract(t1, t2)

		## Initial Order
		init_order = limit_order(direction, quantity, price)

		## Take Profit Order
		tp_delta = 0.02

		take_profit_order = limit_order()

	def at_market(self, action, position, t1, t2):

		## Symbol
		symbol = t1+t2

		## Contract
		contract = forex_contract(t1, t2)

		## Order
		order = market_order(action, position)

		## Execution
		self.placeOrder(self.order_id, contract, order)

		## Request new orderID
		self.reqIds(-1)

		## Start Market Data
		self.reqMktData(tickerId = self.ticker_info[symbol], contract = contract,
						'Mark Price', snapshot = False, regulatorySnapshot = False, [])

		## Init Trade Object
		new_trade = Trade(contract, 1 if action == "BUY" else -1, order)

		## Add to trade dict
		self.trades[symbol] = new_trade

		## Add symbol to trade orderId mapping
		self.order_ids[order.order_id] = self.trades[symbol]

