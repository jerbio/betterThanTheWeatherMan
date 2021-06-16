import sys
import os
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



PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

from libfiles.loaddataseries import load_time_series_daily, load_time_series_daily_from_preClosing, loadIntraDayStockPrices, loadIntraDayAsTimeSeries
from libfiles.weathermanpredictionconfig import WeatherManPredictionConfig
from libfiles.weatherutility import dayIndexFromTime, timeFromDayIndex, getDayIndexByDelta, getSavedFilesFolder


class dayTrader:
  def __init__(self, config:WeatherManPredictionConfig) -> None:
    currentDayTicker = loadIntraDayAsTimeSeries('SPY', None)
    len(currentDayTicker)

    self.closeIndex = ''
    self.openIndex = ''
    self.highIndex = ''
    self.lowIndex = ''
    self.volIndex = ''
    self.avgPriceIndex = ''


  def trade(self):
    '''Application entry point'''
    self.config = WeatherManPredictionConfig()
    self.config.isIntraday=True
    self.config.percentageDeltaChange = 1

  def tickerDataResult(self, tickerData, otherTickerData, config:WeatherManPredictionConfig):
    '''This evaluates the results of ticker based on prices'''
    tickerPrices = [tickerData[self.closeIndex],tickerData[self.openIndex],tickerData[self.highIndex],tickerData[self.lowIndex]]
    avgPrice = None
    if self.avgPriceIndex in tickerData:
      avgPrice = tickerData[self.avgPriceIndex]
    else:
      tickerPrices = [tickerData[self.closeIndex],tickerData[self.openIndex],tickerData[self.highIndex],tickerData[self.lowIndex]]
      avgPrice = sum(tickerPrices)/len(tickerPrices)
      tickerData[self.avgPriceIndex] = avgPrice
    
    pctGoalPrice = avgPrice * (1 + (config.percentageDeltaChange/100))
    result = False
    for ticker in otherTickerData:
      highPrice = ticker[self.highIndex]
      if highPrice >= pctGoalPrice:
        result = True
        break

    return result


  def getTimeOfDaySector(self, tickerData):
    '''Function returns the section of the day the ticker is part of. The time sectors are divided into 4 sections.'''
    tickerTimeString = tickerData['date']
    tradingStartTime = datetime.datetime.strftime(tickerTimeString)
    return 0 #TODO



  def tickerPriceFeature(self, tickerData, previousDayData, correlatingTickerData):
    '''Given a ticker point, this generates the features for the data'''
    retValue = []
    tickerPrices = [tickerData[self.closeIndex],tickerData[self.openIndex],tickerData[self.highIndex],tickerData[self.lowIndex]]
    correlatedPrices = [correlatingTickerData[self.closeIndex],correlatingTickerData[self.openIndex],correlatingTickerData[self.highIndex],correlatingTickerData[self.lowIndex]]
    tickerVolume = tickerData[self.volIndex]
    correlatedTickerVolume = tickerData[self.volIndex]
    averagePrice = sum(tickerPrices)/len(tickerPrices)
    averageCorrelatedPrice = sum(correlatedPrices)/len(correlatedPrices)
    tickerData[self.avgPriceIndex] = averagePrice
    correlatedTimeOfDaySector = self.getTimeOfDaySector(correlatingTickerData)
    timeOfDaySector = self.getTimeOfDaySector(tickerData)
    retValue.append(averagePrice)
    retValue.append(tickerVolume)
    retValue.append(averageCorrelatedPrice)
    retValue.append(correlatedTickerVolume)
    retValue.append(timeOfDaySector)
    retValue.append(correlatedTimeOfDaySector)
    return retValue


  def createDayTradingFeatures(self, symbol, intraDayTicker, previousDayTickerData, config:WeatherManPredictionConfig, correlatingTickerData, stockMetadata = None):
    '''This function takes three parameters, 
    intraDayTicker holds the current intra day ticker price and time, 
    previousDayPrice opening, high, closing price.
    stockMetadata holds stuff like the average price of the stock, average volume, and the stock sector
    correlatingTickerData holds the correlating index fund that tracks the stocks movement. Think SPY and 
      '''

    #https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/
    tickerToSort = {}
    previousDayClose = previousDayTickerData[self.closeIndex]
    tickerFeatures = [tickerData for tickerData in intraDayTicker]
    for index in range(len(intraDayTicker)):
      tickerData = intraDayTicker[index]
      if (index < (len(intraDayTicker) - 1)):
        otherTickers = intraDayTicker[(index+1):]
        precedingTickers = intraDayTicker[:index]
        tickerToSort[tickerData] = {
          'precedingTickers': precedingTickers,
          'otherTickers': otherTickers,
          'features': self.tickerPriceFeature(tickerData, previousDayTickerData, correlatingTickerData),
          'result': self.tickerDataResult(tickerData, otherTickers, config),
          'symbol': symbol
        }

    return tickerToSort

  def evaluateFeatureCardinality(self, tickerDicts):
    return None
