import robin_stocks as r 
import sys
import os
import json
from pathlib import Path

PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from stockpicker import StockPicker
from weathermanpredictionconfig import WeatherManPredictionConfig

#Buy 10 shares of Apple at market price 
# responseResult = r.order_buy_market('BNFT', 1)
# print(str(responseResult))
# r.buy
#Sell half a Bitcoin is price reaches 10,000 
# r.order_sell_crypto_limit('BTC',0.5,10000)
#Buy $500 worth of Bitcoin 
# r.order_buy_crypto_by_price('BTC',500) 
#Buy 5 $150 May 1st, 2020 SPY puts if the price per contract is $1.00. Good until cancelled.
# r.order_buy_option_limit('open','debit',1.00,'SPY',5,'2020-05-01',150,'put','gtc')

class Trader:
    def __init__(self):
        self.credentialFilePath = str(Path('credential.json'))
        self.credData = {}
        self.robinhood = r
        self.loadCredentials()
        config = WeatherManPredictionConfig()
        self.stockPicker = StockPicker(config)
        self.robinhoodStatus()
        
        
        
    def robinhoodStatus(self):
        portfolio = self.robinhood.profiles.load_portfolio_profile()
        buyPower = portfolio['withdrawable_amount']
        print(str(portfolio))

    def loadCredentials(self):
        self.credData = {}
        with open(self.credentialFilePath) as f:
            self.credData = json.load(f)
        robinhoodCredential = self.credData["robinhood"]
        userName = robinhoodCredential["username"]
        password = robinhoodCredential["password"]
        login = r.login(userName, password)

    def getBuyingPower(self):
        portfolio = self.robinhood.profiles.load_portfolio_profile()
        buyPower = portfolio['withdrawable_amount']
        print("Buying power is :" + str(buyPower))
        return buyPower

    def buyStocks(self, symbols, purseValue = None):
        if purseValue is None:
            purseValue = float(self.getBuyingPower())
        if purseValue > 0:
            stockSymbolCount = len(symbols)
            if stockSymbolCount > 0:
                purserPerStockSymbol = purseValue/stockSymbolCount
                for stock in symbols:
                    self.buyStock(stock, purserPerStockSymbol)

    def buyStock(self, stockSymbol, priceLimit):
        pass

    def endOfDayTrade(self):
        stocks = self.stockPicker.getLatestStocksLocal()
        isTodayStocks = []
        for predictionStock in stocks:
            if 'isToday' in predictionStock:
                if predictionStock['isToday'] is True:
                    isTodayStocks.append(predictionStock)
        
        self.buyStocks(isTodayStocks)




