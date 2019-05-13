from ibapi.client import EClient
from ibapi.order import Order

from zcontracts import forex_contract
from zorders import limit_order
from trade import Trade

import queue

import time

class ManagerClient(EClient):

	def __init__(self, wrapper):

		EClient.__init__(self, wrapper = wrapper)

	def at_price(self, price, action, quantity, t1, t2):

		## Trade Direction
		direction = self.action_directions[action]

		## Ticker Symbol
		symbol = t1 + t2

		## IB Contract
		contract = forex_contract(t1, t2)

		## Initial Order
		init_order = limit_order(action, quantity, price)

		## Closing action
		closing_action = self.closing_actions[action]

		## Tick increment
		tick_increment = self.tick_increments[symbol]

		## Take profit order
		tp_target = price + tick_increment * 5
		tp_order = limit_order(closing_action, quantity, tp_target)

		## Soft stop order
		ss_target = price - tick_increment * 5
		ss_order = limit_order(closing_action, quantity, ss_target)

		## Hard stop order
		hs_target = price - tick_increment * 15
		hs_order = limit_order(closing_action, quantity, hs_target)

		## Build Trade Object
		trade = Trade(contract = contract, direction = direction, order = init_order, 
					  orderId = self.order_id, tp_order =  tp_order, ss_order = ss_order, 
					  hs_order = hs_order)
		print('Creating Trade object', trade.symbol, direction)

		## Add trade to position index
		self.trades[symbol] = trade

		## Add trade to reverse index
		self.order_ids[self.order_id] = trade

		## Execute the order
		self.placeOrder(self.order_id, contract, init_order)

		## Increment the next orderID
		self.reqIds(-1)

		## Request Live Quotes
		self.reqMarketDataType(1)

		## Start market data for instrument
		self.reqMktData(self.ticker_ids[symbol], contract, '', False, False, [])

