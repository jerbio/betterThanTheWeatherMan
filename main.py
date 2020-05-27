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


# now = datetime.datetime.now(datetime.timezone.utc)
# eastern = pytz.timezone('America/New_York')
# marketClose = datetime.datetime(now.year, now.month, now.day, 16, 0, 0, tzinfo=eastern)
# # utc_dt = datetime(2009, 7, 10, 18, 44, 59, 193982, tzinfo=pytz.utc)
# coloradoTz = marketClose.astimezone(get_localzone())
# print('colorado '+ str(coloradoTz))
# marketClose.to
# groupSymbolRequest(downloadedSymbols);

# generateModel(WeatherManPredictionConfig(), subSetOfTech[90:153], True);
# loadLatestModel(WeatherManPredictionConfig(), True);
# turnTheKey(WeatherManPredictionConfig(), subSetOfTech[90:153], True);
print("\n\n\nUsing subSetOfTech dataset"); runExec(subSetOfTech[90:153]); print("\n\n\nUsing subSetOfTech dataset"+str(datetime.datetime.now()))
# print("\n\n\nUsing SubsetOfFinance dataset"); runExec(SubsetOfFinance); print("\n\n\nUsing SubsetOfFinance dataset"+str(datetime.datetime.now()))
# print("\n\n\nUsing downloadedSymbols dataset"); runExec(maxSymbols[:50]); print("\n\n\nUsing downloadedSymbols dataset"+str(datetime.datetime.now()))
# # runExec(["AAPL"])
