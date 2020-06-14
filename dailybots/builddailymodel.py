import sys
import os
import time

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.idealpricedsymbols import subSetOfTech
from implementations.weathermanpredictionconfig import WeatherManPredictionConfig
from turnkey import generateModel, loadLatestModel, turnTheKey
from justdownload import downloadDaily, downloadIntraDay


downloadDaily(isMultiThreaded=True, dontDownloadIfExists = False)

minuteSleep = 3
sleepSeconds = minuteSleep * 60
time.sleep(sleepSeconds)
config = WeatherManPredictionConfig()
config.modelRebuildCount = 5
config.numberOfDaysWithPossibleResult = 7
config.percentageDeltaChange = 3
generateModel(config, subSetOfTech[90:153], True)