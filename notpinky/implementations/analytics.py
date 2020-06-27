
import sys
import os
import time

import ast
import matplotlib.pyplot as plt


PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from weatherutility import dayIndexFromTime, timeFromDayIndex

def getTrafficTape(filePath='.\\datafiles\\simultationtape.txt'):
    # filePath = 
    file = open(filePath, "r")
    dictionaryString = file.read()
    dictOfTraffic = ast.literal_eval(dictionaryString)

    dayIndexes = dictOfTraffic.keys()
    dayIndexes = list(dayIndexes)
    dayIndexes.sort()

    completionRateGraph = {}
    cummulativeTotalPredictions = 0
    cummulativeCorrectPredictions = 0
    completionRates = []
    cummulativeCompletionRates = []
    percentageDistribution = {}
    for dayIndex in dayIndexes:
        dayInfo = dictOfTraffic[dayIndex][0]
        correctOnePrediction = dayInfo['correctPredictions']
        totalOnePrediction = dayInfo['totalOnesPredicted']
        completionRate = (correctOnePrediction/totalOnePrediction) * 100
        cummulativeCorrectPredictions += correctOnePrediction
        cummulativeTotalPredictions += totalOnePrediction

        cummulativeCompletionRate = (cummulativeCorrectPredictions/cummulativeTotalPredictions) * 100
        completionRateGraph[dayIndex] = {}
        completionRateGraph[dayIndex]['completionRate'] = completionRate
        completionRateGraph[dayIndex]['cummulativeCompletionRate'] = cummulativeCompletionRate
        completionRates.append(completionRate)
        cummulativeCompletionRates.append(cummulativeCompletionRate)
        if completionRate not in percentageDistribution:
            percentageDistribution[completionRate] = {
                'count': 0,
                'dayIndexes': [],
                'success': [],
                'failure': [],
                'dayIndexToTrades': {}
            }

        tradedStocks = dayInfo['toBeBoughtStocks']
        successStocks = []
        failureStocks = []

        for tradedStock in tradedStocks:
            if tradedStock['result'] == 1:
                successStocks.append(tradedStock)
            else:
                failureStocks.append(tradedStock)


    
        percentageDistribution[completionRate]['count']+=1
        percentageDistribution[completionRate]['dayIndexes'].append(dayIndex)
        percentageDistribution[completionRate]['success'].extend(successStocks)
        percentageDistribution[completionRate]['failure'].extend(failureStocks)

        percentageDistribution[completionRate]['dayIndexToTrades'][dayIndex]={
            'success': successStocks,
            'failure': failureStocks,
            'date': timeFromDayIndex(dayIndex)
        }

    pass


    # plt.plot(dayIndexes, completionRates)
    # plt.show()


getTrafficTape()

pass