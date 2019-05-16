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
		init_order = limit_order(action = action, quantity = quantity, 
						         price = price, purpose = 'initiate')

		## Closing action
		closing_action = self.closing_actions[action]

		## Tick increment
		tick_increment = self.tick_increments[symbol]

		## Take profit order
		tp_target = price + (direction * tick_increment * 1)
		self.logger.warning('\nTake Profit Target: {}'.format(tp_target))
		tp_order = limit_order(action = closing_action, quantity = quantity, 
						       price = tp_target, purpose = 'close')

		## Soft stop order
		ss_target = price - (direction * tick_increment * 1)
		self.logger.warning('Soft Stop Target: {}'.format(ss_target))
		ss_order = limit_order(action = closing_action, quantity = quantity, 
						       price = ss_target, purpose = 'close')

		## Hard stop order
		hs_target = price - (direction * tick_increment * 2)
		self.logger.warning('Hard Stop Target: {}'.format(hs_target))
		hs_order = limit_order(action = closing_action, quantity = quantity, 
						       price = hs_target, purpose = 'close')

		## Build Trade Object
		trade = Trade(contract = contract, direction = direction, order = init_order, 
					  orderId = self.order_id, tp_order = tp_order, ss_order = ss_order, 
					  hs_order = hs_order)

		self.logger.warning('\nCreating Trade Object. Symbol {} Direction {}'.format(trade.symbol, direction))

		## Add trade to position index
		self.trades[symbol] = trade

		## Add order to order index
		self.orders[self.order_id] = init_order

		## Add trade to reverse index
		self.logger.warning('\nAdding ID to reverse index {}'.format(self.order_id))
		self.order_ids[self.order_id] = trade

		## Execute the order
		self.placeOrder(self.order_id, contract, init_order)

		## Increment the next orderID
		self.reqIds(-1)

		## Request Live Quotes
		self.reqMarketDataType(1)

		## Start market data for instrument
		self.reqMktData(self.ticker_ids[symbol], contract, '', False, False, [])

