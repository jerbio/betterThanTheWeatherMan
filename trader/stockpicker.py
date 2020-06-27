import sys
import os
import copy

import datetime

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

import weathermanpredictionconfig
from pathlib import Path


from pathlib import Path

from weatherutility import load_prediction, timeFromDayIndex, dayIndexFromTime

class StockPicker:
    def __init__(self,config:weathermanpredictionconfig, isRemote = False):
        self.isRemote = isRemote
        self.config = config
    def retrieveLatestEligibleStocks(self):
        if self.isRemote:
            return self.getLatestStocksRemote()
        else:
            return self.getLatestStocksLocal()


    def setTodayFlag(self, predictions):
        predictionCopy = copy.deepcopy(predictions)
        currentTime = datetime.datetime.now()
        currentDayIndex = dayIndexFromTime(currentTime)
        for stockPrediction in predictionCopy:
            isToday = stockPrediction['dayIndex'] is currentDayIndex
            stockPrediction['isToday'] = isToday
        return predictionCopy

    def getLatestStocksLocal(self):
        # pathPrefix = '../notpinky/'
        # fullFolderPath = pathPrefix+self.config.predictionFolderTurnedKey
        # fullFolderPath = str(Path(fullFolderPath))
        predictions = load_prediction()
        retValue = self.setTodayFlag(predictions)
        return retValue
        

    def getLatestStocksRemote(self):
        pass
