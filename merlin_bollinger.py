import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from tiingo import TiingoClient
import json
import matplotlib.lines as mlines
import numpy as np


config = {}
config['session'] = True 
config['api_key'] = '6329693b22f8f72d60bc0a13137bf5dd92917a77'
client = TiingoClient(config)

thirty_days_ago = dt.date.today() - dt.timedelta(30)

current = dt.date.today().isoformat()

from urllib.request import urlopen

def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

url = ("https://financialmodelingprep.com/api/v3/stock/actives?apikey=1f700b62f26b1a08aaaa7221930be605")
stocks = get_jsonparsed_data(url)['mostActiveStock']

mostactive = []
for ticker in stocks:
	mostactive.append(ticker['ticker'])

tickers = []
for ticker in client.list_stock_tickers():
	tickers.append(ticker['ticker'])

mostactive = [i for i in mostactive if i in tickers]


#maybe I could use a dictionary that automatically updates to the top 10 stocks every week traded by volume
#and then publish this in a website that shows the bands for these stocks
#df = client.get_dataframe(mostactive[0], metric_name= 'adjClose', frequency='daily', startDate='2015-1-1', endDate=current)

data_frames =[]
i=0
while i < len(mostactive):
	data_frames.append(client.get_dataframe(mostactive[i], frequency='daily', startDate=thirty_days_ago, endDate=current))
	i +=1

for item in data_frames:
	item['30 Day MA'] = item['close'].rolling(window=20).mean()
	item['30 Day STD'] = item['close'].rolling(window=20).std()
	item['Upper Band'] = item['30 Day MA'] + (item['30 Day STD'] * 2)
	item['Lower Band'] = item['30 Day MA'] - (item['30 Day STD'] * 2)
    

for item in data_frames:
    if (np.average(item['Lower Band']) - np.average(item['30 Day MA'])) < (np.average(item['Upper Band']) - np.average(item['30 Day MA'])):
        item['Buy?'] = 'Buy!'
    elif (np.average(item['Lower Band']) - np.average(item['30 Day MA'])) > (np.average(item['Upper Band']) - np.average(item['30 Day MA'])):
        item['Buy?'] = 'No!'
    else:
        item['Buy?'] = 'Maybe?'

for item in data_frames:
    print(item['Buy?'])
