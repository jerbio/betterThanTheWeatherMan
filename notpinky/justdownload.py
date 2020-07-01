from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance, healthcare
from libfiles.downloadstockdata import groupSymbolRequest


intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols.extend(healthcare)
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


# downloadDaily(True, False)


# groupSymbolRequest(maxSymbols, ignoreIfExists = True)
# groupSymbolRequest(subSetOfTech, ignoreIfExists = True)
# groupSymbolRequest(SubsetOfFinance, ignoreIfExists = True)

# runExec(downloadedSymbols)