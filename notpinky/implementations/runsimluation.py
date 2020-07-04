import numpy
import random
import math
import ast


import sys
import os
import time


PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from datafiles.simultationDistribution import indexDistribution
from weatherutility import getSymbolTickerDataForDayIndex, getDayIndexes, timeFromDayIndex, dayIndexFromTime
from libfiles.loaddataseries import load_time_series_daily
from libfiles.idealpricedsymbols import allTheSymbols, turnTheKey, nasdaqPennys, subSetOfTech, healthcare, SubsetOfFinance

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
        self.percentLossSum = 0
        self.percentGainSum = 0
        self.averagePercentLoss = 0
        self.averagePercentGain = 0
        self.useEarlyExit = useEarlyExit #and False
        self.gainCounter = 0
        self.lossCounter = 0
        self.successRatio = 0
        self.nonLoadedDayIndexes = set()
        self.stopLossIsActive = True
        if symbolData is None:
            stocks = list()
            stocks.extend(subSetOfTech)
            #stocks.extend(SubsetOfFinance)
            #stocks.extend(healthcare)
            #stocks.extend(nasdaqPennys)
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
    
    def incrementDayIndex(self, currentDayIndex, delta, symbol):
        isLoadedIndex = False
        # indexOfDays = self.dayIndexToListIndex[currentDayIndex]
        dayIndexes = getDayIndexes(self.symbolData, symbol,currentDayIndex,delta+1 )
        updatedIndex = dayIndexes[len(dayIndexes) - 1]
        if updatedIndex in self.dayIndexToListIndex:
            isLoadedIndex = True
            retValue = updatedIndex
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

    def getEarliestDayDeltaIndexAbovePercentageDelta(self, symbol, currentDayIndex):
        maxDayDelta = self.dayDistribution['dayCount']
        currentDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
        closingPrice = currentDayTicker[3]
        gainPrice = closingPrice * (1+self.percentageDelta)
        formatedIndexes = self.symbolData[symbol]['formatedIndexes']
        dayIndexToListIndex = formatedIndexes['dayIndexToListIndex']
        beginningIndex = dayIndexToListIndex[currentDayIndex]+1
        
        orderedDayIndex = formatedIndexes['orderedDayIndex']
        possibleDayIndexes = orderedDayIndex[beginningIndex:beginningIndex+maxDayDelta]
        dayDeltaCounter = 1
        foundOne = False
        for dayIndex in possibleDayIndexes:
            futureDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, dayIndex)
            futureDayHighPrice = futureDayTicker[2]
            if futureDayHighPrice >= gainPrice:
                foundOne = True
                break
            dayDeltaCounter+=1
        
        if not foundOne:
            raise NameError('You are broken no time in future hits threshold')
        return dayDeltaCounter



    def checkStopLoss(self, symbol, currentDayIndex, dayDelta):
        retValue = {
            'isActivated': False,
            'multiplier': None,
            'updatedDayIndexData': None,
        }
        if self.stopLossIsActive:
            transitionDayIndexes = getDayIndexes(self.symbolData, symbol, currentDayIndex, dayDelta+1)
            transitionDayIndexes.pop(0)
            currentTickerData = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
            purchasePrice = currentTickerData[3]
            percentTrigger = self.percentageDelta #+ 0.1 #- 0.01
            thresholdPrice = purchasePrice * (1 - (percentTrigger))
            stopLossActivated = -1
            dayCounter = 1 # plus because of transitionDayIndexes.pop(0) 
            for transitionDayIndex in transitionDayIndexes:
                tickerPrices = getSymbolTickerDataForDayIndex(self.symbolData, symbol, transitionDayIndex)
                for tickerPrice in tickerPrices[:4]:
                    if tickerPrice < thresholdPrice:
                        stopLossActivated = transitionDayIndex
                        break
                
                if stopLossActivated != -1:
                    break
                dayCounter += 1

            isStopActivated = stopLossActivated != -1
            
            
            if isStopActivated:
                (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, dayCounter, -percentTrigger)
                retValue['isActivated'] = isStopActivated
                retValue['multiplier'] = multiplier
                retValue['updatedDayIndexData'] = updatedDayIndexData

        return retValue


    def executeLoss (self, currentDayIndex, symbol, dayDelta = None, forcePercentDelta = None):
        multiplier = None
        updatedDayIndexData = None
        if self.symbolData is not None and forcePercentDelta is None:
            # multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
            if dayDelta is None:
                dayDelta = self.dayDistribution['dayCount']
            incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
            updatedDayIndexData = incrementResult['dayIndex']
            if not incrementResult['isLoadedIndex']:
                multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
                self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                return (multiplier, updatedDayIndexData)

            currentDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, currentDayIndex)
            nextDayTicker = getSymbolTickerDataForDayIndex(self.symbolData, symbol, updatedDayIndexData)
            percentDelta = (nextDayTicker[3] - currentDayTicker[3])/currentDayTicker[3]
            if percentDelta > .01:
                 percentDelta = 0.0
            multiplier = 1 + percentDelta
            
        else:
            if forcePercentDelta is None:
                multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.2, 1))) )))
            else:
                multiplier = (1 + forcePercentDelta)
            if dayDelta is None:
                dayDelta = self.dayDistribution['dayCount']
            incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
            updatedDayIndexData = incrementResult['dayIndex']
            if not incrementResult['isLoadedIndex']:
                self.addIndexToOrderedDayIndexes(updatedDayIndexData)
                return (multiplier, updatedDayIndexData)

        return (multiplier, updatedDayIndexData)



    def executeTrade(self, stock, availableRatio):
        symbol = stock['symbol']

        multiplier = None
        currentDayIndex = stock['predictionDayIndex']

        isWinTrade = stock['result'] == 1

        overHalfIndex = self.dayDistribution['dayCount'] /2
        overHalfIndex = math.ceil(overHalfIndex)-1


        # try:
        if isWinTrade:
            multiplier = (1 + self.percentageDelta)
            #dayDelta = self.getDayIndexDelta()
            dayDelta = self.getEarliestDayDeltaIndexAbovePercentageDelta(symbol, currentDayIndex)


            earliestDayExit = overHalfIndex if self.useEarlyExit else dayDelta
            stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
            isStopLossActivated = stopLossResult['isActivated']

            if not isStopLossActivated:
                if (self.useEarlyExit and dayDelta > overHalfIndex):
                    (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, overHalfIndex)
                else:
                    incrementResult = self.incrementDayIndex(currentDayIndex, dayDelta, symbol)
                    updatedDayIndexData = incrementResult['dayIndex']
                    if not incrementResult['isLoadedIndex']:
                        self.addIndexToOrderedDayIndexes(updatedDayIndexData)
            else:
                multiplier = stopLossResult['multiplier']
                updatedDayIndexData  = stopLossResult['updatedDayIndexData']
        else:
            earliestDayExit = overHalfIndex if self.useEarlyExit else self.dayDistribution['dayCount']
            stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
            isStopLossActivated = stopLossResult['isActivated']

            if not isStopLossActivated:
                if (self.useEarlyExit):
                    (multiplier, updatedDayIndexData) = self.executeLoss(currentDayIndex, symbol, overHalfIndex)
                    # stopLossResult = self.checkStopLoss(symbol, currentDayIndex, earliestDayExit)
                else:
                    lossResult = self.executeLoss(currentDayIndex, symbol)
                    multiplier = lossResult[0]
                    updatedDayIndexData  = lossResult[1]
            else:
                multiplier = stopLossResult['multiplier']
                updatedDayIndexData  = stopLossResult['updatedDayIndexData']
                
        
        if availableRatio > 0:
            if multiplier < 1:
                self.lossCounter += 1
                self.percentLossSum += (1 - multiplier)
            else:
                self.percentGainSum += (multiplier - 1)
                self.gainCounter += 1
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
        divisor = 1
        countLimit = int((len(self.orderedDayIndexes))/divisor)
        # countLimit = int((len(self.orderedDayIndexes))/2)
        while indexCounter < countLimit:
            dayIndex = self.orderedDayIndexes[indexCounter]
            processedDaIndexes.add(dayIndex)
            self.realizeTrades(dayIndex)
            if(dayIndex in self.simulationTape):
                boughtStocks = self.simulationTape[dayIndex][0]['toBeBoughtStocks']
                if boughtStocks is not None and len(boughtStocks) > 0:
                    numberOfStocks = len(boughtStocks)
                    prevPurse = self.purse
                    pursePerStock = float(((self.purse))/numberOfStocks)
                    for stock in boughtStocks:
                        stockData = stock
                        if 'symbol' not in stock:
                            stockData = stock['lowestPrediction']
                        self.executeTrade(stockData, pursePerStock)
                        self.purse -= pursePerStock
                        if self.purse < 0:
                            self.purse = 0

            indexCounter += 1
            countLimit = int((len(self.orderedDayIndexes))/divisor)


        countLimit = int((len(self.orderedDayIndexes)))
        while indexCounter < countLimit:
            dayIndex = self.orderedDayIndexes[indexCounter]
            processedDaIndexes.add(dayIndex)
            self.realizeTrades(dayIndex)
            indexCounter += 1

        isAllRealized = True
        for tradeDayIndex in self.dayIndexToExecutedTrades:
            isAllRealized = self.dayIndexToExecutedTrades[tradeDayIndex]['isRealized']
            if not isAllRealized:
                print("MAY DAY! MAY DAY!! \n You didn't collect all your profits")
                break
        

        self.successRatio = (self.gainCounter/(self.gainCounter + self.lossCounter)) * 100
        print("all trades were realized " + str(isAllRealized))
        print("success ratio " + str(self.successRatio))

        self.averagePercentLoss = self.percentLossSum/self.lossCounter
        self.averagePercentGain = self.percentGainSum/self.gainCounter

                

def runMultipleSimulations(simulationCount = 500):
    filePath = '.\\datafiles\\simultationtape.txt'
    file = open(filePath, "r")
    contents = file.read()
    indexCounter = 0

    sumOfSimulations = 0

    sumOfAveragesPercentLosses =  0
    sumOfAveragesPercentGains =  0

    minMultiplier = None
    maxMultiplier = None

    percentDelta = 3
    simulationInitObj = WeathermanTimelineSimulator(contents, indexDistribution, percentDelta, 1)
    
    stopLossFlag = False
    earlyExitFlag = False

    while indexCounter < simulationCount:
        moneySimulation = WeathermanTimelineSimulator(contents, indexDistribution, percentDelta, 1, symbolData = simulationInitObj.symbolData, useEarlyExit=True)
        moneySimulation.stopLossIsActive = stopLossFlag
        moneySimulation.useEarlyExit = earlyExitFlag 
        moneySimulation.letsDance()
        sumOfSimulations += moneySimulation.purse
        sumOfAveragesPercentLosses += moneySimulation.averagePercentLoss
        sumOfAveragesPercentGains += moneySimulation.averagePercentGain
        indexCounter+=1

        if minMultiplier is None or moneySimulation.purse < minMultiplier:
            minMultiplier = moneySimulation.purse

        if maxMultiplier is None or moneySimulation.purse > maxMultiplier:
            maxMultiplier = moneySimulation.purse

    averageMultiplier = sumOfSimulations/indexCounter
    averageAveragesPercentLosses = sumOfAveragesPercentLosses/indexCounter
    averageAveragesPercentGains = sumOfAveragesPercentGains/indexCounter
    print('stop Loss is '+str("Active" if stopLossFlag else "Inactive"  ) )
    print('early exit is '+str("Active" if earlyExitFlag else "Inactive"  ) )
    print('average multiplier is '+str(averageMultiplier) )
    print('range of multiplier is '+str(minMultiplier)+' - ' +str(maxMultiplier))
    print('average percentage Loss is '+str(averageAveragesPercentLosses) )
    print('average percentage Gain is '+str(averageAveragesPercentGains) )


runMultipleSimulations(200)