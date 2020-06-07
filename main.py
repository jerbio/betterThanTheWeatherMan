import datetime
from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import  maxSymbols, downloadedSymbols,subSetOfTech,SubsetOfFinance, turnTheKey
from libfiles.downloadstockdata import groupSymbolRequest
import tensorflow as tf
from turnkey import generateModel, loadLatestModel, turnTheKey
import pytz
from tzlocal import get_localzone # $ pip install tzlocal
from implementations.weathermanpredictionconfig import WeatherManPredictionConfig



# tf.test.is_built_with_cuda()

# tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None)


physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# physical_devices = tf.config.list_physical_devices('GPU') 
# tf.config.experimental.set_memory_growth(physical_devices[0], True)


print("\n\n\nUsing subSetOfTech dataset subSetOfTech[90:]"); runExec(subSetOfTech[90:]); print("\n\n\nUsing subSetOfTech dataset subSetOfTech[90:]"+str(datetime.datetime.now()))
# print("\n\n\nUsing SubsetOfFinance dataset SubsetOfFinance[0:72]"); runExec(SubsetOfFinance[0:72]); print("\n\n\nUsing SubsetOfFinance[0:72] dataset "+str(datetime.datetime.now()))
# print("\n\n\nUsing downloadedSymbols dataset"); runExec(maxSymbols[:50]); print("\n\n\nUsing downloadedSymbols dataset"+str(datetime.datetime.now()))
# # runExec(["AAPL"])
