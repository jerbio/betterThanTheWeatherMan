from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance, healthcare, allTheSymbols, nyseInsurance, nyseFinance
from libfiles.downloadstockdata import groupSymbolRequest


intraDaySeriesType = 'TIME_SERIES_INTRADAY'
# symbols = []
# symbols.extend(maxSymbols['symbols'])
# symbols.extend(subSetOfTech['symbols'])
# symbols.extend(SubsetOfFinance['symbols'])
# symbols.extend(healthcare['symbols'])
# symbols = list(set(symbols))

defaultAllSymbols = list(allTheSymbols)


def downloadIntraDay(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    symbolsToBeDownloaded = symbols
    if symbols is None:
        symbolsToBeDownloaded = defaultAllSymbols
    groupSymbolRequest(symbolsToBeDownloaded
    ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)

def downloadDaily(isMultiThreaded=False, dontDownloadIfExists = True, symbols = None):
    symbolsToBeDownloaded = symbols
    if symbols is None:
        symbolsToBeDownloaded = defaultAllSymbols
    groupSymbolRequest(symbolsToBeDownloaded
    # ,series_type=intraDaySeriesType
    , dontDownloadIfExists = dontDownloadIfExists,
    isMultiThreaded=isMultiThreaded)
