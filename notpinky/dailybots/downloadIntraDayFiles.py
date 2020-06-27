import sys
import os
import time

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest


intraDaySeriesType = 'TIME_SERIES_INTRADAY'
allTheSymbols = []
# allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech[90:153])
# allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))
groupSymbolRequest(allTheSymbols, 
    series_type=intraDaySeriesType,
    dontDownloadIfExists = False,
    isMultiThreaded=True)


# groupSymbolRequest(maxSymbols, ignoreIfExists = True)
# groupSymbolRequest(subSetOfTech, ignoreIfExists = True)
# groupSymbolRequest(SubsetOfFinance, ignoreIfExists = True)

# runExec(downloadedSymbols)