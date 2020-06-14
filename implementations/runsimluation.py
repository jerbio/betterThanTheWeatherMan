import numpy
import random

import ast


import sys
import os
import time


PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from datafiles.simultationDistribution import indexDistribution

class WeathermanTimelineSimulator:
    def __init__(self, dictionaryString, dayIndexDistribution, percentageDelta, purse = 100):
        self.purse = purse
        self.percentageDelta = percentageDelta/100
        self.dayIndexToListIndex = {}
        self.orderedDayIndexes = []
        self.simulationTape = self.convertDictionaryStringToDict(dictionaryString)
        self.dayDistribution = self.initializeIndexDistribution(dayIndexDistribution)
        self.dayIndexToExecutedTrades = {}
        self.finalPurse = 0 


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
        orderedDayIndexes = list(dayIndexes)
        orderedDayIndexes.sort()
        index = 0

        for dayIndex in orderedDayIndexes:
            self.dayIndexToListIndex[dayIndex] = index
            index+= 1

        self.orderedDayIndexes = orderedDayIndexes
        return retValue


    def getDayIndexDelta(self):
        retValue = random.choice(self.dayDistribution['randomSequence']) + 1
        return retValue
    
    def incrementDayIndex(self, currentDayIndex, delta):
        indexOfDays = self.dayIndexToListIndex[currentDayIndex]
        updatedIndex = indexOfDays+delta
        retValue = self.orderedDayIndexes[updatedIndex]
        return retValue

    # def getExecutionPrice(self, dayIndex, symbol):
    #     return 0.9999

    def executeTrade(self, stock, availableRatio):
        symbol = stock['symbol']

        executionDayIndex = None
        currentDayIndex = stock['predictionDayIndex']
        

        try:
            if stock['result'] == 1:
                multiplier = (1 + self.percentageDelta)
                dayDelta = self.getDayIndexDelta()
                updatedDayIndexData = self.incrementDayIndex(currentDayIndex, dayDelta)
                executionDayIndex = updatedDayIndexData    
                
            else:
                multiplier = (1 - (((self.percentageDelta * (random.uniform(-0.8, 3.5))) )))
                dayDelta = self.dayDistribution['dayCount'] + 1
                updatedDayIndexData = self.incrementDayIndex(currentDayIndex, dayDelta)
                executionDayIndex = updatedDayIndexData
        except:
            updatedPrice = multiplier * availableRatio
            self.finalPurse += updatedPrice
            return

        updatedPrice = multiplier * availableRatio
        priceUpdates = []
        if updatedDayIndexData in self.dayIndexToExecutedTrades:
            priceUpdates = self.dayIndexToExecutedTrades[updatedDayIndexData]
        else:
            self.dayIndexToExecutedTrades[updatedDayIndexData] = priceUpdates
        
        priceUpdates.append(updatedPrice)


    def realizeTrades(self, dayIndex):
        if dayIndex in self.dayIndexToExecutedTrades:
            priceUpdates = self.dayIndexToExecutedTrades[dayIndex]
            for priceUpdate in priceUpdates: 
                self.purse += priceUpdate

    def letsDance(self):
        dayIndexKeys = list(self.simulationTape.keys())
        dayIndexKeys.sort()
        dayIndexCounter = len(dayIndexKeys)
        dayRandomLimit = 12
        indecounter = random.choices(range(dayRandomLimit))[0]
        while indecounter < dayIndexCounter:
            dayIndex = dayIndexKeys[indecounter]
            self.realizeTrades(dayIndex)
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

            indecounter += 1
        self.finalPurse += self.purse

                

def runMultipleSimulations(simulationCount = 500):
    filePath = '.\\datafiles\\simultationtape.txt'
    file = open(filePath, "r")
    contents = file.read()
    indexCounter = 0

    sumOfSimulations = 0

    minMultiplier = None
    maxMultiplier = None

    while indexCounter < simulationCount:
        moneySimulation = WeathermanTimelineSimulator(contents, indexDistribution, 3, 1)
        moneySimulation.letsDance()
        sumOfSimulations += moneySimulation.finalPurse
        indexCounter+=1

        if minMultiplier is None or moneySimulation.finalPurse < minMultiplier:
            minMultiplier = moneySimulation.finalPurse

        if maxMultiplier is None or moneySimulation.finalPurse > maxMultiplier:
            maxMultiplier = moneySimulation.finalPurse

    averageMultiplier = sumOfSimulations/indexCounter
    print('average multiplier is '+str(averageMultiplier) )
    print('range of multiplier is '+str(minMultiplier)+' - ' +str(maxMultiplier))


runMultipleSimulations()


