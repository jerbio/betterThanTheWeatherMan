import sys
import os
import time

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))


from weathermanpredictionconfig import WeatherManPredictionConfig

liveConfig = WeatherManPredictionConfig()
liveConfig.stockPerDay = 3
liveConfig.preClosingMinuteSpan = 20
liveConfig.numberOfDaysWithPossibleResult = 7
liveConfig.percentageDeltaChange = 3
liveConfig.highValueStocks = False
liveConfig.isOverSampled = False
liveConfig.allowInflectionPoints = False
liveConfig.allowOtherDayFeatures = False
liveConfig.modelRebuildCount = 5
liveConfig.category = 'tech'
liveConfig.exchange = 'nyse'