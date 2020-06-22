import numpy
import random
import math
import ast


import sys
import os
import time


PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from datafiles.simultationDistribution import indexDistribution
from weatherutility import getSymbolTickerDataForDayIndex, getDayIndexes
from libfiles.loaddataseries import load_time_series_daily
from libfiles.idealpricedsymbols import allTheSymbols, turnTheKey, nasdaqPennys, subSetOfTech

class WeathermanTimelineSimulator:
    def __init__(self, dictionaryString, dayIndexDistribution, percentageDelta, purse = 100, symbolData = None, useEarlyExit = True):
        self.purse = purse
        
        self.symbolData = None
        self.percentageDelta = percentageDelta/100
        self.dayIndexToListIndex = {}
        self.orderedDayIndexes = []
        self.simulationTape = self.convertDictionaryStringToDict(dictionaryString)
        self.dayDistribution = self.initializeIndexDistribution(dayIndexDistribution)
        self.dayIndexToExecutedTrades = {}
        self.percentSum = 0
        self.percentCount = 0
        self.averagePercentLoss = 0
        self.useEarlyExit = useEarlyExit
        self.nonLoadedDayIndexes = set()
        if symbolData is None:
            stocks = list()
            stocks.extend(subSetOfTech)
            # stocks.extend(nasdaqPennys)
            stocks.append("TOPS")
            stocks.append("CSPI")
            self.loadAllSymbolTickerDataIntoMemory(stocks)
        else:
            self.symbolData = symbolData


    def loadAllSymbolTickerDataIntoMemory(self, tickerSymbols):
        retValue = {}
        for symbol in tickerSymbols:
            tickerData = load_time_series_daily(symbol)
            retValue[symbol] = tickerData
        self.symbolData = retValue
    

    def initializeIndexDistribution(self, indexDistribution):
        begin = 0
        end = int(len(indexDistribution))

        retValue = {
            'indexBounds': {'begin': begin, 'end': end},
            'distribution': list(indexDistribution),
        }
        retValue['dayCount'] = len(retValue['distribution'])
        retValue['randomSequence'] = random.choices(range(begin, end), weights=retValue['distribution'], k = 1000)
        return retValue

    def convertDictionaryStringToDict(self, dictionaryString):
        retValue = ast.literal_eval(dictionaryString)

        dayIndexes = retValue.keys()
        self.updateDayIndexMapping(dayIndexes)
        self.nonLoadedDayIndexes = set()
        return retValue
        

    def updateDayIndexMapping(self, dayIndexes):
        orderedDayIndexes = list(dayIndexes)
        orderedDayIndexes.sort()
        index = 0
        self.dayIndexToListIndex = {}
        for dayIndex in orderedDayIndexes:
            self.dayIndexToListIndex[dayIndex] = index
            index+= 1

        self.orderedDayIndexes = orderedDayIndexes

    def getDayIndexDelta(self):
        retValue = random.choice(self.dayDistribution['randomSequence']) + 1
        return retValue
    
    def incrementDayIndex(self, currentDayIndex, delta):
        isLoadedIndex = False
        indexOfDays = self.dayIndexToListIndex[currentDayIndex]
        updatedIndex = indexOfDays+delta
        if updatedIndex >= 0 and updatedIndex < len(self.orderedDayIndexes):
            isLoadedIndex = True
            retValue = self.orderedDayIndexes[updatedIndex]
            if retValue in self.nonLoadedDayIndexes:# if dayIndex isn't loaded from storage or read file
                isLoadedIndex = False
        else:
            isLoadedIndex = False
            retValue = currentDayIndex + delta
        return {
            'dayIndex': retValue,
            'isLoadedIndex': isLoadedIndex,
            }

    # def getExecutionPrice(self, dayIndex, symbol):
    #     return 0.9999

    def executeTrade(self, stock, availableRatio):
        symbol = stock['symbol']

        executionDayIndex = None
        multiplier = None
        currentDayIndex = stock['predictionDayIndex']
        currentTickerData = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)

        def executeLoss (self, dayDelta = None, forcePercentDelta = None):
            self.percentCount += 1
            multiplier = None
            updatedDayIndexData = None
            if self.symbolData is not None and forcePercentDelta is None:
                # multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.8, 3.5))) )))
                if dayDelta is None:
                    dayDelta = self.dayDistribution['dayCount']
                incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta)
                updatedDayIndexData = incrementResult['dayIndex']
                if not incrementResult['isLoadedIndex']:
                    multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.8, 3.5))) )))
                    self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                    # updatedPrice = multiplier * availableRatio
                    # self.updateFuturePrice(updatedDayIndexData, updatedPrice)
                    return (multiplier, updatedDayIndexData)

                currentDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
                nextDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, updatedDayIndexData)
                percentDelta = (currentDayTicker[3] - nextDayTicker[3])/currentDayTicker[3]
                self.percentSum += percentDelta
                multiplier = 1 - percentDelta
                
            else:
                if forcePercentDelta is None:
                    multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.8, 3.5))) )))
                else:
                    multiplier = (1 - forcePercentDelta)
                if dayDelta is None:
                    dayDelta = self.dayDistribution['dayCount']
                incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta)
                updatedDayIndexData = incrementResult['dayIndex']
                if not incrementResult['isLoadedIndex']:
                    self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                    return (multiplier, updatedDayIndexData)
                executionDayIndex = updatedDayIndexData

            return (multiplier, updatedDayIndexData)

        # try:
        if stock['result'] == 1:
            multiplier = (1 + self.percentageDelta)
            dayDelta = self.getDayIndexDelta()
            # transitionDayIndexes = getDayIndexes(self.symbolData, symbol, currentDayIndex, dayDelta)
            # transitionDayIndexes.pop(0)
            # purchasePrice = currentTickerData[4]
            # thresholdPrice = purchasePrice * (1 - self.percentageDelta)
            # stopLossActivated = -1
            # dayCounter = 1 # plus because of transitionDayIndexes.pop(0) 
            # for transitionDayIndex in transitionDayIndexes:
            #     tickerPrices = getSymbolTickerDataForDayIndex(self.symbolData, symbol, transitionDayIndex)
            #     for tickerPrice in tickerPrices:
            #         if tickerPrice < thresholdPrice:
            #             stopLossActivated = transitionDayIndex
            #             break
                
            #     if stopLossActivated != -1:
            #         break
            #     dayCounter += 1

            # isStopActivated = stopLossActivated != -1
            # isStopActivated = False
            # if isStopActivated:
            #     (multiplier, updatedDayIndexData) = executeLoss(self, dayCounter, (self.percentageDelta))
            # else:
            overHalfIndex = self.dayDistribution['dayCount'] /2
            overHalfIndex = math.ceil(overHalfIndex) -1
            if (self.useEarlyExit and dayDelta > overHalfIndex):
                (multiplier, updatedDayIndexData) = executeLoss(self, overHalfIndex)
            else:
                incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta)
                updatedDayIndexData = incrementResult['dayIndex']
                if not incrementResult['isLoadedIndex']:
                    self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                    # updatedPrice = multiplier * availableRatio
                    # self.updateFuturePrice(updatedDayIndexData, updatedPrice)
                #     return
                # executionDayIndex = updatedDayIndexData
        else:
            if (self.useEarlyExit):
                overHalfIndex = self.dayDistribution['dayCount'] /2
                overHalfIndex = math.ceil(overHalfIndex) -1 
                (multiplier, updatedDayIndexData) = executeLoss(self, overHalfIndex)
            else:
                lossResult = executeLoss(self)
                multiplier = lossResult[0]
                updatedDayIndexData  = lossResult[1]
                
                
        updatedPrice = multiplier * availableRatio
        self.updateFuturePrice(updatedDayIndexData, updatedPrice)

    def updateFuturePrice(self, updatedDayIndexData, updatedPrice):
        priceUpdates = []
        if updatedDayIndexData in self.dayIndexToExecutedTrades:
            priceUpdateConfig = self.dayIndexToExecutedTrades[updatedDayIndexData]
            priceUpdates = priceUpdateConfig['priceUpdates']
            priceUpdateConfig['isRealized'] = False
        else:
            self.dayIndexToExecutedTrades[updatedDayIndexData] = {
                'priceUpdates': priceUpdates,
                'isRealized': False
            }

        priceUpdates.append(updatedPrice)

    def addIndexToOrderedDayIndexes(self, dayIndex):
        indexes = list(self.orderedDayIndexes)
        indexes.append(dayIndex)
        indexes = list(set(indexes))
        indexes.sort()
        self.nonLoadedDayIndexes.add(dayIndex)
        self.updateDayIndexMapping( indexes)

    def realizeTrades(self, dayIndex):
        if dayIndex in self.dayIndexToExecutedTrades:
            priceUpdateConfig = self.dayIndexToExecutedTrades[dayIndex]
            priceUpdates = priceUpdateConfig['priceUpdates']
            priceUpdateConfig['isRealized'] = True
            for priceUpdate in priceUpdates: 
                self.purse += priceUpdate

    def letsDance(self):
        dayIndexKeys = list(self.simulationTape.keys())
        dayIndexKeys.sort()
        dayIndexCounter = len(dayIndexKeys)
        dayRandomLimit = 12
        indexCounter = random.choices(range(dayRandomLimit))[0]
        # indexCounter = 0
        # indexCounter = int(dayIndexCounter/2)
        processedDaIndexes = set()
        while indexCounter < len(self.orderedDayIndexes):
            dayIndex = self.orderedDayIndexes[indexCounter]
            processedDaIndexes.add(dayIndex)
            self.realizeTrades(dayIndex)
            if(dayIndex in self.simulationTape):
                boughtStocks = self.simulationTape[dayIndex][0]['toBeBoughtStocks']
                if boughtStocks is not None and len(boughtStocks) > 0:
                    numberOfStocks = len(boughtStocks)
                    pursePerStock = float(((self.purse))/numberOfStocks)
                    for stock in boughtStocks:
                        stockData = stock
                        if 'symbol' not in stock:
                            stockData = stock['lowestPrediction']
                        self.executeTrade(stockData, pursePerStock)
                        self.purse -= pursePerStock

            indexCounter += 1

        isAllRealized = True
        for tradeDayIndex in self.dayIndexToExecutedTrades:
            isAllRealized = self.dayIndexToExecutedTrades[tradeDayIndex]['isRealized']
            if not isAllRealized:
                break
        

        # print("all trades were realized " + str(isAllRealized))

        self.averagePercentLoss = self.percentSum/self.percentCount

                

def runMultipleSimulations(simulationCount = 500):
    filePath = '.\\datafiles\\simultationtape.txt'
    file = open(filePath, "r")
    contents = file.read()
    indexCounter = 0

    sumOfSimulations = 0

    sumOfAveragesPercentLosses =  0

    minMultiplier = None
    maxMultiplier = None

    percentDelta = 3
    simulationInitObj = WeathermanTimelineSimulator(contents, indexDistribution, percentDelta, 1)

    while indexCounter < simulationCount:
        moneySimulation = WeathermanTimelineSimulator(contents, indexDistribution, percentDelta, 1, symbolData = simulationInitObj.symbolData, useEarlyExit=True)
        moneySimulation.letsDance()
        sumOfSimulations += moneySimulation.purse
        sumOfAveragesPercentLosses += moneySimulation.averagePercentLoss
        indexCounter+=1

        if minMultiplier is None or moneySimulation.purse < minMultiplier:
            minMultiplier = moneySimulation.purse

        if maxMultiplier is None or moneySimulation.purse > maxMultiplier:
            maxMultiplier = moneySimulation.purse

    averageMultiplier = sumOfSimulations/indexCounter
    averageAveragesPercentLosses = sumOfAveragesPercentLosses/indexCounter
    print('average multiplier is '+str(averageMultiplier) )
    print('range of multiplier is '+str(minMultiplier)+' - ' +str(maxMultiplier))
    print('average percentageLoss is '+str(averageAveragesPercentLosses) )


runMultipleSimulations(500)