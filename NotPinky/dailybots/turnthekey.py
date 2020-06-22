import sys
import os
import time

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.idealpricedsymbols import subSetOfTech
from implementations.weathermanpredictionconfig import WeatherManPredictionConfig
from turnkey import generateModel, loadLatestModel, turnTheKey
import tensorflow as tf



physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

config = WeatherManPredictionConfig()
config.stockPerDay = 3
config.preClosingMinuteSpan = 20
turnTheKey(config, subSetOfTech[90:153], True)