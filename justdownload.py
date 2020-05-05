from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest

groupSymbolRequest(maxSymbols, ignoreIfExists = True)
groupSymbolRequest(subSetOfTech, ignoreIfExists = True)

# runExec(downloadedSymbols)