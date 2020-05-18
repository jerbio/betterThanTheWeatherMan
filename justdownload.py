from libfiles.idealpricedsymbols import maxSymbols, subSetOfTech, SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest


allTheSymbols = []
allTheSymbols.extend(maxSymbols)
allTheSymbols.extend(subSetOfTech)
allTheSymbols.extend(SubsetOfFinance)
allTheSymbols = list(set(allTheSymbols))
groupSymbolRequest(allTheSymbols, dontDownloadIfExists = False)


# groupSymbolRequest(maxSymbols, ignoreIfExists = True)
# groupSymbolRequest(subSetOfTech, ignoreIfExists = True)
# groupSymbolRequest(SubsetOfFinance, ignoreIfExists = True)

# runExec(downloadedSymbols)