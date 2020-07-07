import robin_stocks as r 
import sys
import os
import json
import math
from pathlib import Path

PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from stockpicker import StockPicker
from weathermanpredictionconfig import WeatherManPredictionConfig
from weatherutility import getRealtimeStockPrice

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
        self.excludedStocks = set()
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
        allowedSymbols = set()
        for eachSymbol in symbols:
            if eachSymbol['symbol'] not in self.excludedStocks:
                allowedSymbols.add(eachSymbol['symbol'])

        if purseValue is None:
            purseValue = float(self.getBuyingPower())
        if purseValue > 0:
            stockSymbolCount = len(allowedSymbols)
            if stockSymbolCount > 0:
                purserPerStockSymbol = purseValue/stockSymbolCount
                for stockSymbol in allowedSymbols:
                    symbol = stockSymbol
                    latestStockInfo = getRealtimeStockPrice(symbol)
                    if latestStockInfo and len(latestStockInfo) > 0 and ('last' in latestStockInfo[0]):
                        latestPrice = latestStockInfo[0]['last']
                        limitPrice = latestPrice
                        self.buyStockByBudget(symbol, purserPerStockSymbol, limitPrice)

    def buyStockByBudget(self, stockSymbol, orderBudget, limitPrice = None):
        pricePerStock = limitPrice
        if limitPrice is None:
            latestStockInfo = getRealtimeStockPrice(stockSymbol)
            if latestStockInfo and len(latestStockInfo) > 0 and ('last' in latestStockInfo[0]):
                latestPrice = latestStockInfo[0]['last']
                pricePerStock = latestPrice
                
        
        shareCount =  math.floor(orderBudget/pricePerStock)
        if shareCount > 1:
            self.buyStockByCount(stockSymbol, shareCount, limitPrice)
        pass

    def buyStockByCount(self, stockSymbol, quantity, limitPrice = None):
        retValue = None
        if limitPrice is None:
            print("Placed an order for "+str(quantity) + " of "+ str(stockSymbol))
            retValue = self.robinhood.order_buy_market(stockSymbol, quantity, extendedHours= True)
        else:
            print("Placed an order for "+str(quantity) + " of "+ str(stockSymbol) + " at limit price $" + str(limitPrice))
            retValue = self.robinhood.order_buy_limit(stockSymbol, quantity, limitPrice=limitPrice, extendedHours= True)
        
        return retValue

    def addToAvoidedStocks(self, stockSymbol):
        if stockSymbol:
            self.excludedStocks.add(stockSymbol.upper())

    def removeFromAvoidedStocks(self, stockSymbol):
        if stockSymbol:
            self.excludedStocks.remove(stockSymbol.upper())

    def endOfDayTrade(self):
        stocks = self.stockPicker.getLatestStocksLocal()
        isTodayStocks = []
        for predictionStock in stocks:
            if 'isToday' in predictionStock:
                if predictionStock['isToday'] is True:
                    isTodayStocks.append(predictionStock)
        
        self.buyStocks(isTodayStocks)




