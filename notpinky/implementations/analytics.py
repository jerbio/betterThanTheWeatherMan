
import sys
import os
import time

import math
import ast
import matplotlib.pyplot as plt


PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from weatherutility import dayIndexFromTime, timeFromDayIndex, getDayIndexes
from libfiles.loaddataseries import load_time_series_daily
from libfiles.idealpricedsymbols import subSetOfTech, healthcare


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
                'dayIndexes': set(),
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
        percentageDistribution[completionRate]['dayIndexes'].add(dayIndex)
        percentageDistribution[completionRate]['success'].extend(successStocks)
        percentageDistribution[completionRate]['failure'].extend(failureStocks)

        percentageDistribution[completionRate]['dayIndexToTrades'][dayIndex]={
            'success': successStocks,
            'failure': failureStocks,
            'date': timeFromDayIndex(dayIndex)
        }


    # plt.plot(dayIndexes, completionRates)
    # plt.show()

    return {'completionRateGraph': completionRateGraph, 'percentageDistribution': percentageDistribution}


    


graphData = getTrafficTape()

def getTickerWithinWindow(stock, allSymbolsToTickerData, dayCount):
    symbol = stock['symbol']
    dayIndex = stock['predictionDayIndex']
    dayIndexes = getDayIndexes(allSymbolsToTickerData, symbol, dayIndex, dayCount)
    retValue = {}
    for dayIndex in dayIndexes:
        tickerData = allSymbolsToTickerData[symbol]['symbolData'][dayIndex]['ticker']
        retValue[dayIndex] = tickerData

    return retValue

dayDelta = 4
percentaageDelta = 3


def stopLossAssesment(completionRateGraph, percentageDistribution, tickerSymbols, stockFlag = 0):
    ''' stockFlag arg 0 -> failures, 1-> success, any other number -> combine both '''
    allSymbolsToTickerData = {}
    for symbol in tickerSymbols:
        tickerData = load_time_series_daily(symbol)
        allSymbolsToTickerData[symbol] = tickerData

    dayIndexToTickerData = {}
    for completionRate in percentageDistribution:
        dayIndexes = percentageDistribution[completionRate]['dayIndexes']
        for dayIndex in dayIndexes:
            successStocks = percentageDistribution[completionRate]['dayIndexToTrades'][dayIndex]['success']
            failureStocks = percentageDistribution[completionRate]['dayIndexToTrades'][dayIndex]['failure']

            stockCombination = list()
            if stockFlag == 0:
                stockCombination = list(failureStocks)
            else:
                if stockFlag == 1:
                    stockCombination = list(successStocks)
                else:
                    stockCombination = list(successStocks)
                    stockCombination.extend(failureStocks)

            # stockCombination.extend(successStocks)
            # stockCombination = list(failureStocks)
            # stockCombination.extend(failureStocks)
            
            for stock in stockCombination:
                symbol = stock['symbol']
                subSequentDayTicker = getTickerWithinWindow(stock, allSymbolsToTickerData, dayDelta)
                # orderedKeys = list(subSequentDayTicker.keys())
                # orderedKeys.sort()
                # currentDayKey = orderedKeys.pop(0)
                # del subSequentDayTicker[currentDayKey]
                dayIndexToSubSequentDayTicker = {}
                if dayIndex not in dayIndexToTickerData:
                    dayIndexToTickerData[dayIndex] = dayIndexToSubSequentDayTicker
                else:
                    dayIndexToSubSequentDayTicker = dayIndexToTickerData[dayIndex]
                dayIndexToSubSequentDayTicker[symbol] = subSequentDayTicker


    return dayIndexToTickerData


def evaluateDistribution(dayIndexToTickerData):
    priceDeltaSum = 0
    priceDeltaCount = 0
    percentDistribution = {}
    swingBackSuccess = {}

    for dayIndex in dayIndexToTickerData:
        dayIndexToSubsequentTickers = dayIndexToTickerData[dayIndex]
        for symbol in dayIndexToSubsequentTickers:
            allTickerData = []
            subSequentDayTickerData = dayIndexToSubsequentTickers[symbol]
            orderedDayIndexes = list(subSequentDayTickerData.keys())
            orderedDayIndexes.sort()
            tradeDayIndex = orderedDayIndexes[0]
            tradeDayTicker = subSequentDayTickerData[tradeDayIndex]
            tradeDayClosePrice = tradeDayTicker[3]
            successQuotient = 1 + (percentaageDelta/100)
            successTradePrice = tradeDayClosePrice * successQuotient
            for subSequentDayIndex in orderedDayIndexes:
                if subSequentDayIndex != tradeDayIndex:
                    tickerData = subSequentDayTickerData[subSequentDayIndex]
                    allTickerData.extend(tickerData)
                    subsequentDayLowPrice = tickerData[1]
                    subsequentDayHighPrice = tickerData[2]
                    if subsequentDayHighPrice < successTradePrice:
                        percentDelta = ((subsequentDayLowPrice - tradeDayClosePrice)/tradeDayClosePrice) * 100
                        percentDeltaFloor = math.floor(percentDelta)
                        if percentDeltaFloor not in percentDistribution:
                            percentDistribution[percentDeltaFloor] = 0
                    else:
                        break
                    
                    percentDistribution[percentDeltaFloor] += 1
                    priceDeltaCount+=1
                    priceDeltaSum += percentDelta

    lowPercentAverageDelta = priceDeltaSum/priceDeltaCount
    print('Percent delta '+ str(lowPercentAverageDelta))
    print('Percent delta distribution '+ str(percentDistribution))
    percentFloors = list(percentDistribution.keys())
    percentFloors.sort()
    percentCardinality = []
    for percentFloor in percentFloors:
        count = percentDistribution[percentFloor]
        percentCardinality.append(count)
    
    plt.plot(percentFloors, percentCardinality)
    plt.show()


dayIndexToTickerData = stopLossAssesment(graphData['completionRateGraph'], graphData['percentageDistribution'], healthcare['symbols'], stockFlag=0)

evaluateDistribution(dayIndexToTickerData)
pass