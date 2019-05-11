from ibapi.order import Order

def default_order(action, quantity):

	order = Order()
	order.action = action
	order.totalQuantity = quantity
	return order

def market_order(action, quantity, price):

	order = default_order(action, quantity)
	order.orderType = 'MKT'
	return order

def limit_order(action, quantity, price):

	order = default_order(action, quantity)
	order.orderType = "LMT"
	order.lmtPrice = price
	return order

def market_if_touched(action, quantity, price):

	order = default_order(action, quantity)
	order.orderType = "MIT"
	order.auxPrice = price

	return order

def limit_if_touched(action, quantity, limit_price, trigger_price):

	order = default_order(action, quantity)
	order.orderType = "LIT"
	order.lmtPrice = limit_price
	order.auxPrice = trigger_price
