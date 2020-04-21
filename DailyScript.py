from libfiles.downloadStockData import downloadStockBySymbol
from libfiles.loadDataSeries import load_time_series_daily
import matplotlib.pyplot as plt 

stockGroupings = {
    "technologySW": ["GOOG", "MSFT", "FB", "AMZN", "AAPL", "NFLX", "TWTR"],
    "technologyHW": ["INTC","AMD", "TSM", "SNE"],
    "finance": ["MS", "GS", "BAC"],
    "travel": ["AAL", "DAL", "UAL"],
    "weed": ["CRON", "ACB", "CBDS"],
    "retail": ["WMT", "TGT", "WBA"]
    }
filePath = "d:\\WeatherManDump"
for key in stockGroupings:
    seriesType = "TIME_SERIES_INTRADAY"
    stockSymbols = stockGroupings[key]
    for symbol in stockSymbols:
        downloadStockBySymbol(symbol, seriesType, filePath) # This downloads the time ticker data



