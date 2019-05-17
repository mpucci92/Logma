import numpy as np

from ibapi.client import EClient
from ibapi.order import Order

from zcontracts import forex_contract
from zorders import limit_order
from trade import Trade

import queue, time

class ManagerClient(EClient):

	def __init__(self, wrapper):

		EClient.__init__(self, wrapper = wrapper)

	def on_signal(self, action, quantity, t1, t2, price):

		## Ticker Symbol
		symbol = t1 + t2

		## IB Contract
		contract = forex_contract(t1, t2)

		## Tick increment
		tick_increment = self.tick_increments[symbol]

		## Direction
		direction = self.action_directions[action]

		## Adjust the price for min tick increment rule
		price = self.adjust_price(price, tick_increment, direction)

		## Initial Order
		initial_order = limit_order(action = action, quantity = quantity, 
									price = price, purpose = 'initiate')

		## Closing details
		closing_details = {
			"take_profit" : price + (direction * tick_increment * 4),
			"soft_stop" : price - (direction * tick_increment * 4),
			"hard_stop" : price - (direction * tick_increment * 8)
		}

		## Build Trade Object
		trade = Trade(manager = self, contract = contract, action = action,
					  initial_order = initial_order, closing_details = closing_details)

		## Add trade to position index
		self.trades[symbol] = trade

		## Request Live Quotes
		self.reqMarketDataType(1)

		## Start market data for instrument
		self.reqMktData(self.ticker_ids[symbol], contract, '', False, False, [])

	def adjust_price(self, price, tick_incr, direction, margin = True, base=5):

		## Add a 1 tick buffer
		price += tick_incr / base * direction if margin else 0
		
		## Round the price
		price = 0.1 + price / (tick_incr / base) * direction
		price = base * np.floor(price/base) * direction

		return price / (base / tick_incr)

