
from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest
import os
import datetime
from pathlib import Path

intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))

# groupSymbolRequest(allTheSymbols,
#     filePath='../EstimateTrainingData/StockDump/'
#     , dontDownloadIfExists = False)


beforeDownloadTime = datetime.datetime.now()




groupSymbolRequest(allTheSymbols,
    filePath = str(Path('../EstimateTrainingData/StockDump/')
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = False,
    isMultiThreaded=True)

    

afterDownloadTime = datetime.datetime.now()

downloadTimeSpan = (afterDownloadTime - beforeDownloadTime)
print('download took a total of ' + str(downloadTimeSpan))





