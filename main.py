import datetime
from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import  maxSymbols, downloadedSymbols,subSetOfTech,SubsetOfFinance
from libfiles.downloadstockdata import groupSymbolRequest
import tensorflow as tf
# tf.test.is_built_with_cuda()

# tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None)


physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# physical_devices = tf.config.list_physical_devices('GPU') 
# tf.config.experimental.set_memory_growth(physical_devices[0], True)




# groupSymbolRequest(downloadedSymbols);

print("\n\n\nUsing subSetOfTech dataset"); runExec(subSetOfTech[:50]); print("\n\n\nUsing subSetOfTech dataset"+str(datetime.datetime.now()))
# print("\n\n\nUsing SubsetOfFinance dataset"); runExec(SubsetOfFinance); print("\n\n\nUsing SubsetOfFinance dataset"+str(datetime.datetime.now()))
# print("\n\n\nUsing downloadedSymbols dataset"); runExec(maxSymbols[:50]); print("\n\n\nUsing downloadedSymbols dataset"+str(datetime.datetime.now()))
# # runExec(["AAPL"])
