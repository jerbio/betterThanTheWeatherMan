from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import downloadedSymbols,subSetOfTech,SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest
import tensorflow as tf
physical_devices = tf.config.list_physical_devices('GPU') 
tf.config.experimental.set_memory_growth(physical_devices[0], True)
# groupSymbolRequest(downloadedSymbols);

runExec(downloadedSymbols)