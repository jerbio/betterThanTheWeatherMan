from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest

intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))
groupSymbolRequest(allTheSymbols,
    filePath='..\\EstimateTrainingData\\StockDump\\'
    # ,series_type=intraDaySeriesType
    , dontDownloadIfExists = False)

# groupSymbolRequest(allTheSymbols,
#     filePath='..\\EstimateTrainingData\\StockDump\\'
#     ,series_type='TIME_SERIES_INTRADAY'
#     , dontDownloadIfExists = False)
