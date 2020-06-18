from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance, nasdaqPennys
from libfiles.downloadstockdata import groupSymbolRequest


intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols.extend(nasdaqPennys)
allTheSymbols = list(set(allTheSymbols))






def downloadIntraDay(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    if symbols is None:
        symbols = allTheSymbols
    groupSymbolRequest(allTheSymbols
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)

def downloadDaily(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    if symbols is None:
        symbols = allTheSymbols

    groupSymbolRequest(symbols
    # ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)


downloadDaily(True, False)


# groupSymbolRequest(maxSymbols, ignoreIfExists = True)
# groupSymbolRequest(subSetOfTech, ignoreIfExists = True)
# groupSymbolRequest(SubsetOfFinance, ignoreIfExists = True)

# runExec(downloadedSymbols)