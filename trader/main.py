import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from weathermanpredictionconfig import WeatherManPredictionConfig
from trader import Trader
from stockpicker import StockPicker


# config = WeatherManPredictionConfig()
# stockpicker = StockPicker(config)

# latestStocks = stockpicker.getLatestStocksLocal()
# print(str(latestStocks))


botTrader = Trader()
botTrader.addToAvoidedStocks("bcov")
botTrader.addToAvoidedStocks("egan")
stocks = list()
# stocks.append("PLAB")
# stocks.append("BNFT")
# stocks.append("ICHR")
# stocks.append("AOSL")
# stocks.append("CRTO")
# stocks.append("VNET")
# botTrader.buyStocks(stocks)
botTrader.endOfDayTrade()
# activeOrders = botTrader.getInvestedStockPositions();
# pendingOrders = botTrader.getPendingOrders();
# botTrader.testRequest();

