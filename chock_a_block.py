import requests
import time
import json


apikey = '9dc03fd90ea65219b348a5c97f6de0580efb7bf9'
venue = 'TESTEX'
stock = 'FOOBAR'
base_url = "https://api.stockfighter.io/ob/api/"
account = 'EXB123456'

shares_remaining = 100000
current_cash = 0

#key: ticker, value:qty
my_holdings = {}

#keep track of orders. Important info: order ID, price, quantity
#should be a dict of tuples
# {order id: (price,quantity)}

my_buys = {}
my_sells = {}
def to_buy(remaining):
	if remaining < 500:
		return remaining
	return 500

def buy(account,venue,stock,order_type):

	payload ={
		'account': account,
		'venue': venue,
		'stock': stock,
		'qty': to_buy(shares_remaining),
		'direction': "buy",
		'orderType': order_type 
		}
	r = requests.post(base_url+"venues/"+venue+"/stocks/"+stock+"/orders",json=payload, headers={"X-Starfighter-Authorization":apikey})
	data = r.json()
	try: 
		data['symbol'].assertEquals(stock)
	except AssertionError as e:
		print "They gave us the wrong shit!!! {}".format(e)
		print "Got {} instead of {}".format(r.json['symbol'],stock)

	for fill in data['fills']:
		cash = cash - fill['price']
		my_holdings[stock] += fill['qty']



def get_quote(venue, stock):
	quote = requests.get(base_url+"venues/"+venue+"/stocks/"+stock+"/quote")
	return quote.json()

def sell(account,venue,stock,order_type):
	payload ={
		'account': account,
		'venue': venue,
		'stock': stock,
		'qty': to_buy(shares_remaining),
		'direction': "sell",
		'orderType': order_type 
		}
	r = requests.post(base_url+"venues/"+venue+"/stocks/"+stock+"/orders",json=payload, headers={"X-Starfighter-Authorization":apikey})

	for fill in data['fills']:
		cash = cash + fill['price']
		my_holdings[stock] -= fill['qty']	

def cancel(venue,stock,order_number):
	r = requests.delete(base_url+"venues/"+venue+"/stocks/"+stock+"/orders/"+order_number, headers={"X-Starfighter-Authorization":apikey})
	return r.json()

def get_orderbook(venue,stock):
	r = requests.get(base_url+"venues/"+venue+"/stocks/"+stock)
	return r.json()

def get_orderbook_minus_my_orders(venue,stock):
	r = requests.get(base_url+"venues/"+venue+"/stocks/"+stock)
	bids = r.json()['bids']

	for order, value in my_orders:
		for bid in bids:
			if value[0]==bid['price'] and value[1]==bid['qty']:
				bids.remove(bid)			
	return bids

r = requests.get(base_url+"/heartbeat")
print "API status: ", r.status_code

try:
	# stock_list = requests.get(base_url+"venues/"+venue+"/stocks")
	# # parsed_stocks = stocks.json()
	# print stock_list.text

	# orderbook = requests.get(base_url+"venues/"+venue+"/stocks/"+stock)
	# print orderbook.text

	quote = requests.get(base_url+"venues/"+venue+"/stocks/"+stock+"/quote")
	print quote.text
	start_price = quote.json()['bid']
	print "Best price is {}".format(start_price)
except Exception as e:
	print "There was a problem: {}".format(e)


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

# while current_cash < 10000:



# 	time.sleep(5)



