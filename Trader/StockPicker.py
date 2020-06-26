import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from pathlib import Path

class StockPicker:
    def __init__(self, isRemote = False):
        self.isRemote = isRemote
    def retrieveLatestEligibleStocks():
        if self.isRemote:
            return self.getLatestStocksRemote()
        else:
            return self.getLatestStocksLocal()


    def getLatestStocksLocal():
        
        

    def getLatestStocksRemote():

