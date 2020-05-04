from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest

groupSymbolRequest(SubsetOfFinance, ignoreIfExists = False)

# runExec(downloadedSymbols)