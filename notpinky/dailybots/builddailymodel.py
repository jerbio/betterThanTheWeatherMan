import sys
import os
import time

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.idealpricedsymbols import subSetOfTech, symbolDictionary
from weathermanpredictionconfig import WeatherManPredictionConfig
from turnkey import generateModel, loadLatestModel, turnTheKey
from liveConfig import liveConfig
from justdownload import downloadDaily, downloadIntraDay


# minuteSleep = 3
# sleepSeconds = minuteSleep * 60
# time.sleep(sleepSeconds)

# config.modelRebuildCount = 5
# config.numberOfDaysWithPossibleResult = 7
# config.percentageDeltaChange = 3
# config.highValueStocks = False
# config.isOverSampled = False
# config.allowInflectionPoints = False
# config.allowOtherDayFeatures = False


def generateModelByConfig(liveConfig, category, exchange):
    liveConfig.category = category
    liveConfig.exchange = exchange
    liveConfig.allowInflectionPoints = False
    liveConfig.allowOtherDayFeatures = False
    generateModel(liveConfig, symbolDictionary[liveConfig.category][liveConfig.exchange], True)
    liveConfig.allowInflectionPoints = True
    liveConfig.allowOtherDayFeatures = True
    generateModel(liveConfig, symbolDictionary[liveConfig.category][liveConfig.exchange], False)

stockGrouping = [('tech','nasdaq'),('health','nasdaq')]

for entry in stockGrouping:
    category = entry[0]
    exchange = entry[1]
    generateModelByConfig(liveConfig, category, exchange)

