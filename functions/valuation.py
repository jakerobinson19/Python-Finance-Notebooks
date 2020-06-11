# valuation.py

#import necessary packages
import pandas as pd
import json
import requests

# Plotly visualization packages
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def format_data(data):
	data.date = data.date.astype('datetime64')
	data = data.drop(['link',
			'finalLink',
			'symbol',
			'acceptedDate'], axis=1).T
	data.columns = data.iloc[0].astype(str).str[:10]
	data = data[1:]
	del data.columns.name

	return(data)

def generate_url(ticker, api_key, p_type, statement):
	return('https://financialmodelingprep.com/api/v3/{}/{}?period={}&apikey={}'.format(statement, ticker, p_type, api_key))

def historical_prices(ticker, api_key):
	url = 'https://financialmodelingprep.com/api/v3/historical-price-full/{}?&apikey={}'.format(ticker,api_key)
	p = requests.get(url)

	prices_json = json.loads(p.text)
	try:
		prices = pd.DataFrame(prices_json["historical"], columns=['date','open','high','low','close']).set_index('date')

	except:
		log_error("Historical Prices Are Not Available at this time", prices_json)
		prices = None

	return(prices)

def plot_historical_price_chart(ticker, api_key):
	p = get_historical_prices(ticker, api_key)

	fig = go.Figure(data=[go.Candlestick(x=p.index,
                	open=p['open'],
                	high=p['high'],
                	low=p['low'],
               		close=p['close'])])

	fig.update_layout(
    			title="{} Stock Chart".format(ticker),
    			xaxis_title="Year",
    			yaxis_title="Price")

	fig.show()
	
def profile(ticker, api_key):
	url = generate_url(ticker, api_key, '0', 'profile')

	profile = pd.read_json(url)
	profile = profile.T
	del profile.columns.name

	return(profile)

def quote(ticker, api_key):
	url = generate_url(ticker, api_key, '0', 'quote')

	quote = pd.read_json(url)
	quote = quote.T
	del quote.columns.name

	quote.columns = [ticker]
	quote = quote.loc[['name', 'exchange',
			   'price','yearHigh',
			   'yearLow','marketCap',
			   'volume','eps','pe',
			   'sharesOutstanding']]
	quote.index = ['Name','Exchange',
		       'Price','52-wk High',
		       '52 wk Low','Market Cap',
		       'Volume','EPS','P/E',
		       'Shares Outstanding']

	return(quote)

def balance_sheet(ticker, api_key, p_type, periods): #periods
	url = generate_url(ticker, api_key, p_type, 'balance-sheet-statement')

	b_sheet = pd.read_json(url)
	balance_sheet = format_data(b_sheet)

	return(balance_sheet.iloc[:, : periods])

def income_statement(ticker, api_key, p_type): #periods
	url = generate_url(ticker, api_key, p_type, 'income-statement')

	inc_statement = pd.read_json(url)
	income_statement = format_data(inc_statement)

	return(income_statement)

def cash_flow_statement(ticker, api_key, p_type, periods):
	url = generate_url(ticker, api_key, p_type, 'cash-flow-statement')

	cf_statement = pd.read_json(url)
	cashflow_statment = format_data(cf_statement)

	return(cashflow_statment.iloc[:, : periods])

def plot_annual_cashflows(ticker, years, api_key):
	cf = get_cash_flow_statement(ticker, api_key, 'annual', years)

	fig = make_subplots(rows=1, cols=1, start_cell="top-left")

	fig.add_trace(go.Bar(name="Cash Flows", 
                    	x=cf.columns, 
                    	y=cf.iloc[-1], 
                    	text=cf.iloc[-1], 
                    	textposition='outside', 
                    	marker_color='#2ca02c',
                    	texttemplate = "$%{text:,.0f}"), 
              			row=1, col=1)

	fig.update_layout(
   				title="{} Cash Flows".format(ticker),
    			xaxis_title="Year",
    			yaxis_title="Dollars")

	fig.show()

def get_historical_dividends(ticker, api_key):
	url = 'https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{}?apikey={}'.format(ticker, api_key)

	d = requests.get(url)

	divs_json = json.loads(d.text)
	try:
		dividends = pd.DataFrame(divs_json["historical"], columns=['date','adjDividend']).set_index('date')

	except:
		log_error("Historical Dividends Are Not Available at this time", divs_json)
		dividends = None

	return(dividends)

def fcf_per_share(ticker, api_key):
	return(cashflow_statement(ticker, api_key, 'annual', 5).iloc[-1][0]/quote(ticker, api_key).loc['Shares Outstanding'][0])

def get_eps(ticker, api_key):
	return(quote(ticker, api_key).loc['EPS'][0])

def discount_calculation(g_rate, g_years, t_rate, t_years, discount_rate):
	x = (1+g_rate)/(1+discount_rate)
	y = (1+t_rate)/(1+discount_rate)

	try:
		z = x * (1-x**10)/(1-x) + (x**10)*y*(1-y**10)/(1-y)
	except:
		growth_contrib = 0
		term_contrib = 0
    
	for i in range(g_years):
		growth_contrib += x**(i+1)
        
	for i in range(t_years):
		term_contrib += y**(i+1)
    
	term_contrib = (x**g_years)*term_contrib
        
	return(growth_contrib + term_contrib)

def discounted_cash_flow(ticker, g_rate, g_years, t_rate, t_years, discount_rate, api_key):
	fcf_per_share = fcf_per_share(ticker, api_key)

	z = discount_calculation(g_rate, g_years, t_rate, t_years, discount_rate)

	return(fcf_per_share*z)

def eps_valuation(ticker, g_rate, g_years, t_rate, t_years, discount_rate, api_key):
	eps = get_eps(ticker, api_key)

	z = discount_calculation(g_rate, g_years, t_rate, t_years, discount_rate)

	return(eps*z)
