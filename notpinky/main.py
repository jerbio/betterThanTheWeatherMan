import datetime
from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import  maxSymbols, subSetOfTech,SubsetOfFinance, nasdaqPennys, healthcare, symbolDictionary
from libfiles.downloadstockdata import groupSymbolRequest
import tensorflow as tf
from turnkey import generateModel, loadLatestModel, turnTheKey
import pytz
from tzlocal import get_localzone # $ pip install tzlocal
from weathermanpredictionconfig import WeatherManPredictionConfig
import requests
import json


# tf.test.is_built_with_cuda()

# tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None)


config = WeatherManPredictionConfig()

# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
# # import os
# # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# # physical_devices = tf.config.list_physical_devices('GPU') 
# # tf.config.experimental.set_memory_growth(physical_devices[0], True)

config.category = 'manufacturing'
config.exchange = 'nyse'
config.highValueStocks = False
config.allowInflectionPoints = True
config.allowOtherDayFeatures = True
config.highLowStockValueSplitRatio = 2
config.stockPerDay = 3
config.percentageDeltaChange = 3
config.numberOfDaysWithPossibleResult = 7
print("\n\n\nUsing "+str(config.category)+" for "+str(config.exchange)+" exchange\nBegan At"); 
runExec(config, symbolDictionary[config.category][config.exchange])
print("\n\n\nUsing "+str(config.category)+" for "+str(config.exchange)+" exchange\nEnded At"+str(datetime.datetime.now()))

