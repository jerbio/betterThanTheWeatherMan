from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import subSetOfTech,SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest

groupSymbolRequest(SubsetOfFinance, ignoreIfExists = True)

# runExec(downloadedSymbols)