import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from weathermanpredictionconfig import WeatherManPredictionConfig
from StockPicker import StockPicker


config = WeatherManPredictionConfig()
stockpicker = StockPicker(config)

stockpicker.getLatestStocksLocal()