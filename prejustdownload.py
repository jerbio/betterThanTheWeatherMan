from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest
from pathlib import Path

intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))

# groupSymbolRequest(allTheSymbols,
#     filePath=str(str(Path('../EstimateTrainingData/StockDump/'))
#     , dontDownloadIfExists = False)


groupSymbolRequest(allTheSymbols,
    filePath= str(Path('../EstimateTrainingData/StockDump/'))
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = False)


