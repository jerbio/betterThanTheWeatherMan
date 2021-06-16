import datetime
import pytz
import requests
import json
import os
import sys
import tensorflow as tf

# PACKAGE_PARENT = '../../'
# SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from implementations.onlypositivedeltas import runExec
from libfiles.idealpricedsymbols import  maxSymbols, subSetOfTech,SubsetOfFinance, nasdaqPennys, healthcare, symbolDictionary
from libfiles.downloadstockdata import groupSymbolRequest
from libfiles.weathermanpredictionconfig import WeatherManPredictionConfig





# tf.test.is_built_with_cuda()

# tf.test.is_gpu_available(cuda_only=False, min_cuda_compute_capability=None)


config = WeatherManPredictionConfig()

# physical_devices = tf.config.list_physical_devices('GPU')
# tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)
# # import os
# # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# # physical_devices = tf.config.list_physical_devices('GPU') 
# # tf.config.experimental.set_memory_growth(physical_devices[0], True)


config.category = 'tech'
config.exchange = 'nasdaq'
# config.epochCount = 500
config.highValueStocks = False
config.allowInflectionPoints = True
config.allowOtherDayFeatures = True
config.highLowStockValueSplitRatio = 2
config.stockPerDay = 6
config.percentageDeltaChange = 3
config.numberOfDaysWithPossibleResult = 7
config.numberOfDaysForTraining = 180
config.numberOfRetroDays = 240
config.layer = [512, 512]
config.daysExceddingLimits = 3
print("\n\n\nUsing "+str(config.category)+" for "+str(config.exchange)+" exchange\nBegan At"); 
runExec(config, symbolDictionary[config.category][config.exchange])
print("\n\n\nUsing "+str(config.category)+" for "+str(config.exchange)+" exchange\nEnded At"+str(datetime.datetime.now()))

