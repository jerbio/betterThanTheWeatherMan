import sys
import os
import json
import datetime
import random
import tensorflow as tf
from pathlib import Path



PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

from libfiles.loaddataseries import load_time_series_daily, load_time_series_daily_from_preClosing, loadIntraDayStockPrices
from libfiles.weathermanpredictionconfig import WeatherManPredictionConfig
from libfiles.weatherutility import dayIndexFromTime, timeFromDayIndex, getDayIndexByDelta, getSavedFilesFolder

from daytradertrainer import DayTraderTrainer


config = WeatherManPredictionConfig
trainer = DayTraderTrainer(config)
trainer.initializeTrainingELements()

trainer.train()