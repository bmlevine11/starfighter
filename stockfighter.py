import config
import requests
import time
import json


apikey = config.apikey

venue = 'SRGEX'
stock = 'OXES'
account = 'FPS22000719'
base_url = "https://api.stockfighter.io/ob/api/"

cash = 0

#key: ticker, value:qty. Should probably have price I paid in here too
my_holdings = {}

#keep track of orders. Important info: order ID, price, quantity
#should be a dict of tuples
# {order id: (price,quantity,type,open)}

my_buys = {}
my_sells = {}

market_buys = {}
market_sells = {}

def to_buy(remaining):
	if remaining < 500:
		return remaining
	return 500

def buy(account,venue,stock,order_type,qty,price):

	payload ={
		'account': account,
		'venue': venue,
		'stock': stock,
		'qty': qty,
		'direction': "buy",
		'orderType': order_type,
		'price': price
		}
	r = requests.post(base_url+"venues/"+venue+"/stocks/"+stock+"/orders",json=payload, headers={"X-Starfighter-Authorization":apikey})
	data = r.json()
	global my_buys
	my_buys[data['id']] = (data['price'],data['qty'],data['orderType'],data['open'])
	# try:
	# 	assert data['symbol'] == stock
	# except AssertionError as e:
	# 	print "They gave us the wrong shit!!! {}".format(e)
	# 	print "Got {} instead of {}".format(r.json['symbol'],stock)

	for fill in data['fills']:
		global cash, my_holdings
		cash -= fill['price']
		try:
			my_holdings[stock] += fill['qty']
		except KeyError:
			my_holdings[stock] = fill['qty']


def get_quote(venue, stock):
	quote = requests.get(base_url+"venues/"+venue+"/stocks/"+stock+"/quote")
	return quote.json()

def sell(account,venue,stock,order_type,qty,price):
	payload ={
		'account': account,
		'qty': qty,
		'direction': "sell",
		'orderType': order_type,
		'price': price
		}
	r = requests.post(base_url+"venues/"+venue+"/stocks/"+stock+"/orders",json=payload, headers={"X-Starfighter-Authorization":apikey})
	data = r.json()

	my_sells[data['id']] = (data['price'],data['qty'],data['orderType'],data['open'])

	for fill in data['fills']:
		global cash, my_holdings
		cash += fill['price']
		my_holdings[stock] -= fill['qty']

def cancel(venue,stock,order_number):
	r = requests.delete(base_url+"venues/"+venue+"/stocks/"+stock+"/orders/{}".format(order_number), headers={"X-Starfighter-Authorization":apikey})
	global my_buys
	global my_sells
	try:
		my_buys.pop(order_number)
	except KeyError:
		my_sells.pop(order_number,None)

	return r.json()

def get_orderbook(venue,stock):
	global market_buys, market_sells
	r = requests.get(base_url+"venues/"+venue+"/stocks/"+stock)
	market_buys = r.json()['bids']
	market_sells = r.json()['asks']

	return r.json()

def get_orderbook_minus_my_orders(venue,stock):
	global market_buys, market_sells

	get_orderbook(venue, stock)

	for order, value in my_buys.iteritems():
		for bid in market_buys:
			if value[0]==bid['price'] and value[1]==bid['qty']:
				market_buys.remove(bid)
	for order, value in my_sells.iteritems():
		try:
			for ask in market_sells:
				if value[0]==ask['price'] and value[1]==ask['qty']:
					market_sells.remove(ask)
		except:
			print "No sell orders"

def average_sell():
	global market_sells
	total_value = 0

	for ask in market_sells:
		total_value += ask['price']
	try:
		average = total_value/float(len(market_sells))
	except:
		average = None
	return average


def average_buy():
	global market_buys
	total_value = 0
	for bid in market_buys:
		total_value += bid['price']

	try:
		average = total_value/float(len(market_buys))
	except:
		average = 0

	return average

r = requests.get(base_url+"/heartbeat")
print "API status: ", r.status_code

# try:
# 	# stock_list = requests.get(base_url+"venues/"+venue+"/stocks")
# 	# # parsed_stocks = stocks.json()
# 	# print stock_list.text

# 	# orderbook = requests.get(base_url+"venues/"+venue+"/stocks/"+stock)
# 	# print orderbook.text

# 	quote = requests.get(base_url+"venues/"+venue+"/stocks/"+stock+"/quote")
# 	print quote.text
# 	start_price = quote.json()['bid']
# 	print "Best price is {}".format(start_price)
# except Exception as e:
# 	print "There was a problem: {}".format(e)


# while shares_remaining > 0:
# 	quote = requests.get(base_url+"venues/"+venue+"/stocks/"+stock+"/quote")
# 	try:
# 		current_price = quote.json()['bid']
#  	except KeyError as key_error:
# 		current_price = quote.json()['ask']

# 	if current_price < (start_price+300):
# 		buy(account, venue, stock, "market" )
# 		print r.text
# 		shares_remaining = shares_remaining - r.json()['totalFilled']
# 	else:
# 		print "Price out of range: ${}".format(current_price)
# 	print "Shares Remaining: {}".format(shares_remaining)
# 	time.sleep(1)

get_orderbook(venue, stock)

while cash < 100000:

	get_orderbook_minus_my_orders(venue,stock)

	avg_buy = average_buy()
	avg_sell = average_sell()

	my_buy_price = market_buys[-1]['price'] + 10

	try:
		my_sell_price = avg_sell - 10
	except:
		my_sell_price = my_buy_price + 50

	temp_buys = {order:value for order,value in my_buys.iteritems()}
	for order, value in temp_buys.iteritems():
		if value[0] > my_buy_price:
			cancel(venue, stock, order)

	temp_sells = {order:value for order,value in my_sells.iteritems()}
	for order, value in temp_sells.iteritems():
		if value[0] < my_sell_price:
			cancel(venue, stock, order)

	if my_buy_price < avg_buy:
		b = buy(account, venue, stock, 'limit', 500, int(my_buy_price))

	if my_sell_price > avg_buy:
		print my_holdings
		if my_holdings and my_holdings['stock']['qty'] < 500:
			s = sell(account, venue, stock, 'limit', my_holdings['stock']['qty'], int(my_sell_price))
		else:
			s = sell(account, venue, stock, 'limit', 500, int(my_sell_price))



	print "Current Cash: {}".format(cash)
	print "Average buy price: {}".format(avg_buy)
	print "My buy price: {}".format(my_buy_price)
	print "Average sell price: {}".format(avg_sell)
	print "My sell price: {}".format(my_sell_price)
	time.sleep(5)
