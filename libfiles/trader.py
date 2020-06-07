import robin_stocks as r 
import sys
import os
import json

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))




portfolio = r.profiles.load_portfolio_profile()
buyPower = portfolio.withdrawable_amount

print(str(portfolio))
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
        self.filePath = 'creds.json'
        self.credData = {}
        self.robinhood = r
        self.loadCredentials()
        

    def loadCredentials(self):
        self.credData = {}
        with open(self.filePath) as f:
            self.credData = json.load(f)
        robinhoodCredential = self.credData["robinhood"]
        login = r.login(robinhoodCredential["username"], robinhoodCredential["password"])

    # def 
    



