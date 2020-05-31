
# from libfiles.downloadstockdata import downloadStockBySymbol
# from libfiles.loaddataseries import load_time_series_daily
# import matplotlib.pyplot as plt 

# from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
# from libfiles.downloadstockdata import groupSymbolRequest

# stockGroupings = {
#     "technologySW": ["GOOG", "MSFT", "FB", "AMZN", "AAPL", "NFLX", "TWTR"],
#     "technologyHW": ["INTC","AMD", "TSM", "SNE"],
#     "finance": ["MS", "GS", "BAC"],
#     "travel": ["AAL", "DAL", "UAL"],
#     "weed": ["CRON", "ACB", "CBDS"],
#     "retail": ["WMT", "TGT", "WBA"]
#     }
# # filePath = "d:\\WeatherManDump"
# seriesType = "TIME_SERIES_INTRADAY"
# # for key in stockGroupings:
    
# #     stockSymbols = stockGroupings[key]

# allTheSymbols = []
# # allTheSymbols.extend(maxSymbols)
# # allTheSymbols.extend(subSetOfTech)
# allTheSymbols.extend(SubsetOfFinance[90:153])
# allTheSymbols = list(set(allTheSymbols))
# for symbol in allTheSymbols:
#     downloadStockBySymbol(symbol, seriesType, ignoreIfExists=False) # This downloads the time ticker data

from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest
import os
import datetime

intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))

# groupSymbolRequest(allTheSymbols,
#     filePath='..\\EstimateTrainingData\\StockDump\\'
#     , dontDownloadIfExists = False)


beforeDownloadTime = datetime.datetime.now()




groupSymbolRequest(allTheSymbols,
    filePath='..\\EstimateTrainingData\\StockDump\\'
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = False,
    isMultiThreaded=True)

    

afterDownloadTime = datetime.datetime.now()

downloadTimeSpan = (afterDownloadTime - beforeDownloadTime)
print('download took a total of ' + str(downloadTimeSpan))





