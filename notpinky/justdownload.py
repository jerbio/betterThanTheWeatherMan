from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance, healthcare
from libfiles.downloadstockdata import groupSymbolRequest


intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols['symbols'])
allTheSymbols.extend(subSetOfTech['symbols'])
allTheSymbols.extend(SubsetOfFinance['symbols'])
allTheSymbols.extend(healthcare['symbols'])
allTheSymbols = list(set(allTheSymbols))




def downloadIntraDay(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    symbolsToBeDownloaded = allTheSymbols
    if symbols is not None:
        symbolsToBeDownloaded = allTheSymbols
    groupSymbolRequest(symbolsToBeDownloaded
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)

def downloadDaily(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    symbolsToBeDownloaded = allTheSymbols
    if symbols is not None:
        symbolsToBeDownloaded = allTheSymbols
    groupSymbolRequest(symbolsToBeDownloaded
    # ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)


