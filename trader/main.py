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
botTrader.addToAvoidedStocks("ssys")
botTrader.addToAvoidedStocks("comm")
# botTrader.endOfDayTrade()
activeOrders = botTrader.getInvestedStockPositions();
pendingOrders = botTrader.getPendingOrders();
botTrader.testRequest();

