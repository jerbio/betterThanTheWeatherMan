import json
import datetime
import random
import tensorflow as tf
from pathlib import Path
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
import math
import matplotlib.pyplot as plt
from numpy import array, transpose

import sys
import os

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


currentDayTicker = loadIntraDayStockPrices('BNTC')
len(currentDayTicker)


def createDayTradingFeatures(intraDayTicker, previousDayPrice, stockMetadata, correlatingTickerData):
  '''This function takes three parameters, 
  intraDayTicker holds the current intra day ticker price and time, 
  previousDayPrice opening, high, closing price.
  stockMetadata holds stuff like the average price of the stock, average volume, and the stock sector
  correlatingTickerData holds the correlating index fund that tracks the stocks movement. Think SPY and 
    '''
  
  