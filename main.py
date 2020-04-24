from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import downloadedSymbols
from libfiles.downloadstockdata import groupSymbolRequest

# groupSymbolRequest(downloadedSymbols);

runExec(downloadedSymbols)