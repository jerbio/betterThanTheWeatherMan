import json
import datetime
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
import math
import matplotlib.pyplot as plt
from numpy import array, transpose

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.loaddataseries import load_time_series_daily
from .weathermanpredictionconfig import WeatherManPredictionConfig
from weatherutility import dayIndexFromStart, timeFromDayIndex

# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
# config.log_device_placement = True  # to log device placement (on which device the operation ran)
#                                     # (nothing gets printed in Jupyter, only if you run it standalone)
# sess = tf.Session(config=config)
# set_session(sess)  # set this TensorFlow session as the default session for Keras


def  precedingDayIndexes(currentDayIndex, dayCount, tickerDictionary):
    '''gets the X number of days prior to currentDayIndex within the tickerDictionary. X is determined by dayCount'''
    retValue = []
    cons_loop_counter = 7 # seven because a stock might not have data for a week
    maxCountLoop = cons_loop_counter
    validDayIndex = currentDayIndex - 1
    while validDayIndex not in tickerDictionary and maxCountLoop > 0:
        validDayIndex -= 1
        maxCountLoop -= 1
    
    maxCountLoop = cons_loop_counter
    insertedDayCount = 0
    while maxCountLoop > 0 and insertedDayCount < dayCount:
        if validDayIndex in tickerDictionary:
            insertedDayCount +=1
            retValue.append(validDayIndex)
        else:
            maxCountLoop -= 1
        
        validDayIndex-=1
    
    return retValue



def getPreceedingDayInflectionFeatures(dayIndex, timeData):
    earliestDay = dayIndex - 91
    dayIndexesDict = {}
    tickerInfo = timeData[dayIndex]
    loopDayIndex = dayIndex
    foundEarliestDay = False
    while not foundEarliestDay:
        sevenDayIndexes = precedingDayIndexes(loopDayIndex, 7, timeData)
        maxPriceKey = 'highprice'
        lowPriceKey = 'lowprice'
        dayIndexesDict[loopDayIndex] = {
            'indexes': sevenDayIndexes,
            ''+maxPriceKey+'': None,
            ''+lowPriceKey+'': None
        }

        if len(sevenDayIndexes) == 0:
            print("YOUZ about to fail")
            print("Failing day index is " + str(loopDayIndex))
            allKeys = list(timeData.keys())
            allKeys.sort()
            precedingDayIndexes(loopDayIndex, 7, timeData)
            # print( allKeys)
            # return None
            
            # precedingDayIndexes(loopDayIndex, 7, timeData)
        
        loopEarliestDay = sevenDayIndexes[len(sevenDayIndexes) -1]
        if loopEarliestDay > earliestDay:
            loopDayIndex = loopEarliestDay - 1
        else:
            foundEarliestDay = True
            break

    allMaxes = []
    for key in dayIndexesDict:
        dayIndexes = dayIndexesDict[key]['indexes']
        maxPrices = [(index, timeData[index]["ticker"][1], timeData[index]["ticker"][2]) for index in dayIndexes]
        maxEntry = []
        minEntry = []
        for priceTuple in maxPrices:# gets the highest and minimum for the given week
            if len(maxEntry) == 0 or maxEntry[1] < priceTuple[2]:
                maxEntry = [priceTuple[0], priceTuple[2]]
            if len(minEntry) == 0 or minEntry[1] > priceTuple[1]:
                minEntry = [priceTuple[0], priceTuple[1]]

        if len(maxEntry) != 0: 
            dayIndexesDict[key][maxPriceKey] = maxEntry
        if len(minEntry) != 0: 
            dayIndexesDict[key][lowPriceKey] = minEntry
    
    allvalues = list(dayIndexesDict.values())
    
    inflextionCount = 7
    sortedByHigh =sorted(allvalues, key=lambda highPrice: highPrice[maxPriceKey][1])
    sortedByLow =sorted(allvalues, key=lambda lowPrice: lowPrice[lowPriceKey][1])

    highestInflexionPoints = sortedByHigh[len(sortedByHigh)-inflextionCount:]
    highestInflexionPoints = sorted(highestInflexionPoints, key=lambda inflextionPoint: inflextionPoint[maxPriceKey][0])#sorts by day index
    lowestInflextionPoints = sortedByLow[:inflextionCount]
    lowestInflextionPoints = sorted(lowestInflextionPoints, key=lambda inflextionPoint: inflextionPoint[lowPriceKey][0])#sorts by day index
    openPrice = tickerInfo['ticker'][0]
    lowestPrice = tickerInfo['ticker'][1]
    highestPrice = tickerInfo['ticker'][2]
    closePrice = tickerInfo['ticker'][3]
    avgPrice = tickerInfo['ticker'][4]
    
    def getFeatureForInflection(inflexionPoints):
        dayDeltas = []
        currentDayDiff = 0
        diffBetweenDeltas = []
        avgPriceGradient = []
        lowPriceGradient = []
        highestPriceGradient = []
        averageDayDelta = 0
        mostRecentDayDelta = inflexionPoints[len(inflexionPoints) - 1][0] - dayIndex
        for inflexionPoint in inflexionPoints:
            inflexionDayIndex = inflexionPoint[0]
            inflexionDayPrice = inflexionPoint[1]
            if dayIndex != inflexionDayIndex:
                dayDiff = dayIndex - inflexionPoint[0] 
                dayDeltas.append(dayDiff)
                diffBetweenDelta = dayDiff - currentDayDiff
                diffBetweenDeltas.append(diffBetweenDelta)
                currentDayDiff = dayDiff
                gradientAvgPriceForDay = (avgPrice - inflexionDayPrice)/dayDiff
                avgPriceGradient.append(gradientAvgPriceForDay)
                gradientLowPriceForDay = ((lowestPrice - inflexionDayPrice)/dayDiff) *100
                lowPriceGradient.append(gradientLowPriceForDay)
                gradientHighPriceForDay = ((highestPrice - inflexionDayPrice)/dayDiff)*100
                highestPriceGradient.append(gradientHighPriceForDay)

        if len(diffBetweenDeltas) != 0:
            averageDayDelta = (sum(diffBetweenDeltas)/len(diffBetweenDeltas)) * 100
        averagePriceDelta = (sum(avgPriceGradient)/len(avgPriceGradient)) * 100
        retValue = []
        
        retValue.append(averageDayDelta)
        retValue.extend(avgPriceGradient)
        retValue.append(averagePriceDelta)
        # retValue.extend(diffBetweenDeltas)
        # retValue.extend(dayDeltas)
        # retValue.append(mostRecentDayDelta)
        # retValue.extend(highestPriceGradient)
        # retValue.extend(lowPriceGradient)
        return retValue



    highestInflextionPointFeatures = getFeatureForInflection(
        [[data[maxPriceKey][0], data[maxPriceKey][1]] for data in highestInflexionPoints]
        )
    lowestInflextionPointsFeatures = getFeatureForInflection(
        [[data[lowPriceKey][0], data[lowPriceKey][1]] for data in lowestInflextionPoints]
        )

    retValue = [lowestInflextionPointsFeatures,
                 highestInflextionPointFeatures
                 ]
    return retValue

def getPrecedingDay(dayIndex, tickerData):
    retryCounterLimit = 7
    retryCounter = 0
    retValue = -1
    precedingDayIndex = dayIndex - 1
    while retryCounter < retryCounterLimit:
        if precedingDayIndex in tickerData:
            retValue = precedingDayIndex
            break
        precedingDayIndex -= 1
        retryCounter += 1
    return retValue

def getNextDayIndex(dayIndex, tickerData):
    retryCounterLimit = 7
    retryCounter = 0
    retValue = None
    precedingDayIndex = dayIndex + 1
    while retryCounter < retryCounterLimit:
        if precedingDayIndex in tickerData:
            retValue = precedingDayIndex
            break
        precedingDayIndex += 1
        retryCounter += 1
    return retValue



def getRetroDayTrainingData(config:WeatherManPredictionConfig, tickerData, symbolIndex, dayOfPrediction):
    dayCountForFeatures = config.numberOfRetroDays
    precedingNintyDays = []
    possibleRetroDay = int(dayOfPrediction) - dayCountForFeatures
    retryCount = 7
    foundEarliestDay = False
    featureLen = -1
    tickerFeaturesPerDay = -1
    allRetroDayIndexes = set()
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = None
    retroTrainingDays = 0

    # dayOfPrediction = int(day)

    day = int(dayOfPrediction)

    openPrice = tickerData[day]["ticker"][0]
    highPrice = tickerData[day]["ticker"][2]
    lowPrice = tickerData[day]["ticker"][1]
    closePrice = tickerData[day]["ticker"][3]
    refPrice = openPrice


    while retryCount > 0: #gets the earliest day before or equal to 'dayCountForFeatures' thats within tickerData
        if possibleRetroDay in tickerData:
            foundEarliestDay = True
            break
        possibleRetroDay -= 1
        retryCount -= 1
    if foundEarliestDay:
        while possibleRetroDay < dayOfPrediction:
            if possibleRetroDay in tickerData:
                featureDay = beginningOfTime + datetime.timedelta(days=(possibleRetroDay))
                weekDay = featureDay.weekday()
                retroDayTickerData = tickerData[possibleRetroDay]
                dataForDay = [] #[symbolCounter, possibleRetroDay]
                fiveDayAvgPriceDelta = None
                previousDayCountLimit = 4
                previousDayCounter = previousDayCountLimit
                previousDayCount = possibleRetroDay
                previousDayCountLoopLimit = previousDayCountLimit + 4
                finalPreviousDayIndex = possibleRetroDay
                tradingDayCount = 0
                allRetroDayIndexes.add(possibleRetroDay)

                retroDayOpeningPrice = retroDayTickerData['ticker'][0]
                retroDayClosingPrice = retroDayTickerData['ticker'][3]
                retroDayHighPrice = retroDayTickerData['ticker'][2]
                retroDayLowPrice = retroDayTickerData['ticker'][1]
                retroDayAvgPrice = retroDayTickerData['ticker'][4]
                # volume = retroDayTickerData["ticker"][5]
                
                while previousDayCounter > 0 and previousDayCountLoopLimit > 0:
                    previousDayCount -=1
                    if previousDayCount in tickerData:
                        previousDayCounter -= 1
                        finalPreviousDayIndex = previousDayCount
                        tradingDayCount += 1
                    previousDayCountLoopLimit -= 1

                # predictionDayHighDeltaPercent = ((highPrice - refPrice) / refPrice) * 100
                # predictionDayOpenDeltaPercent = ((openPrice - refPrice) / refPrice) * 100
                # predictionDayLowDeltaPercent = ((lowPrice - refPrice) / refPrice) * 100
                # dataForDay.append(predictionDayHighDeltaPercent)
                # dataForDay.append(predictionDayOpenDeltaPercent)
                # dataForDay.append(predictionDayLowDeltaPercent)
                
                avgPriceCategory = int((retroDayAvgPrice)/10)
                dataForDay.append(avgPriceCategory)


                openPricePredictionDayDelta = retroDayOpeningPrice - refPrice
                closePricePredictionDayDelta = retroDayClosingPrice - refPrice
                highPricePredictionDayDelta = retroDayHighPrice - refPrice
                lowPricePredictionDayDelta = retroDayLowPrice - refPrice
                avgPricePredictionDayDelta = retroDayAvgPrice - refPrice

                openPricePredictionDayDeltaPercent = (openPricePredictionDayDelta/refPrice) * 100
                closePricePredictionDayDeltaPercent = (closePricePredictionDayDelta/refPrice) * 100
                highPricePredictionDayDeltaPercent = (highPricePredictionDayDelta/refPrice) * 100
                lowPricePredictionDayDeltaPercent = (lowPricePredictionDayDelta/refPrice) * 100
                avgPricePredictionDayDeltaPercent = (avgPricePredictionDayDelta/refPrice) * 100
                
                dataForDay.append(openPricePredictionDayDeltaPercent)
                dataForDay.append(closePricePredictionDayDeltaPercent)
                dataForDay.append(highPricePredictionDayDeltaPercent)
                dataForDay.append(lowPricePredictionDayDeltaPercent)
                dataForDay.append(avgPricePredictionDayDeltaPercent)
                


                openLowDelta = retroDayLowPrice - retroDayOpeningPrice
                openHighDelta = retroDayHighPrice - retroDayOpeningPrice
                highLowDelta = retroDayHighPrice - retroDayLowPrice

                percentHighDelta = (openHighDelta / retroDayOpeningPrice) * 100
                percentOpenLowDelta = (openLowDelta / retroDayOpeningPrice)*100
                percentHighLowDelta = (highLowDelta / retroDayOpeningPrice)*100

                percentCloseDelta = (openHighDelta / retroDayClosingPrice)* 100
                percentCloseLowDelta = (openLowDelta / retroDayClosingPrice) * 100
                percentCloseHighDelta = (highLowDelta / retroDayClosingPrice) * 100
                dataForDay.append(percentCloseDelta)
                dataForDay.append(percentCloseLowDelta)
                dataForDay.append(percentCloseHighDelta)
                dataForDay.append(percentHighDelta)
                dataForDay.append(percentOpenLowDelta)
                dataForDay.append(percentHighLowDelta)
                
                

                openCloseDelta = retroDayClosingPrice - retroDayOpeningPrice
                if previousDayCounter != previousDayCountLimit:
                    previousDayTickerEntry = tickerData[finalPreviousDayIndex]
                    fiveDayAvgPriceDelta = (retroDayAvgPrice - previousDayTickerEntry['ticker'][4])
                percentOpenCloseDelta = (openCloseDelta / retroDayOpeningPrice) *100
                dataForDay.append(percentOpenCloseDelta)
                tradingDayDelta = 0
                percentageTradingDayDelta = 0
                if fiveDayAvgPriceDelta is None:
                    percentFiveDayDelta = percentOpenCloseDelta
                else:
                    percentFiveDayDelta = (fiveDayAvgPriceDelta/retroDayOpeningPrice)
                    tradingDayDelta = fiveDayAvgPriceDelta/tradingDayCount
                    percentageTradingDayDelta = ((fiveDayAvgPriceDelta/retroDayOpeningPrice) * 100)/tradingDayCount
                
                dataForDay.append(percentFiveDayDelta)
                dataForDay.append(tradingDayDelta)
                dataForDay.append(percentageTradingDayDelta)

                dataForDay.append(retroDayOpeningPrice)
                dataForDay.append(retroDayLowPrice)
                dataForDay.append(retroDayHighPrice)
                dataForDay.append(retroDayClosingPrice)
                dataForDay.append(retroDayAvgPrice)
                # dataForDay.append(weekDay)

                inflectionPointFeatures = getPreceedingDayInflectionFeatures(dayOfPrediction, tickerData)
                if inflectionPointFeatures is not None:
                    for precedingDayInflectionFeatures in inflectionPointFeatures:
                        dataForDay.extend(precedingDayInflectionFeatures)
                    precedingNintyDays.extend(dataForDay)
                    retroTrainingDays +=1
                featureLen = len(dataForDay)
                if tickerFeaturesPerDay < featureLen:
                    tickerFeaturesPerDay = featureLen            
            possibleRetroDay +=1
        
        precedingNintyDays = slicePrecedingDaysToStandardLength(precedingNintyDays, tickerFeaturesPerDay, dayCountForFeatures)
        if precedingNintyDays is not None:
            retValue = {
                        "day": day,
                        "retroDays": allRetroDayIndexes,
                        "precedingDays": precedingNintyDays,
                        "featureLengthPerRetroDay": featureLen,
                        "symbolIndex": symbolIndex,
                        "tickerFeaturesPerDay": tickerFeaturesPerDay,
                        "retroTrainingDays": retroTrainingDays
                    }
    

    return retValue

def getDayOutlook(config:WeatherManPredictionConfig, tickerData, earliestDay = None, latestDay = None, symbolIndex = 0):
    '''
    function gets X consecutive future days of stock data within the time frame of 'earliestDay  and 'latestDay' data. 
    X is provided with the arg 'dayCount'. These day points have to be within tickerData.
    This function returns an object that contains the preceding Y days of features.
    Y is provided by 'dayCountForFeatures'
    '''
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {
    }

    dayCountForFeatures = config.numberOfRetroDays
    dayCount = config.numberOfOutlookDays
    tickerFeaturesPerDay = -1
    trainingDays = set()
    earliestDayInt = 0
    latestDayInt = 0
    if earliestDay:
        earliestDayInt = (earliestDay - beginningOfTime).days
    
    if latestDay:
        latestDayInt = (latestDay - beginningOfTime).days
    else:
        currentTime = datetime.datetime.now()
        latestDay = currentTime + datetime.timedelta(days=(0))
        latestDayInt = (latestDay - beginningOfTime).days

    beginDayIndex = earliestDayInt
    latestDayIndex = latestDayInt
    currentDayIndex = beginDayIndex

    while currentDayIndex < latestDayIndex:
        day = currentDayIndex
        if day in tickerData:
            currentDay = beginningOfTime + datetime.timedelta(days=(day))
            dayOfPrediction = int(day)
            openPrice = tickerData[day]["ticker"][0]
            closePrice = tickerData[day]["ticker"][3]
            highPrice = tickerData[day]["ticker"][2]
            lowPrice = tickerData[day]["ticker"][1]
            refPrice = closePrice
            
            nextDaySeriesIndexes = []
            nextDaySeriesChanges = []
            precedingNintyDays = []
            counter = 0
            activeDayCounter = 0
            isNegative = False
            highestDelta = 0
            ignoreDay = True
            maxPositive = 0
            maxNegative = 0
            allRetroDayIndexes = set()
            notIncludedDays = set()
            notIncludedDays.add(day)
            # nextDayIndex = getNextDayIndex(day, tickerData)
            # if nextDayIndex is not None:
            #     notIncludedDays.add(nextDayIndex)
            retryLimit = dayCount + 2 #we assume 2 days for weekend + the occasional 2days for back to back holidays and 1 for the logic dayIndex != day which ignores the current prediction day
            while counter < retryLimit and len(nextDaySeriesIndexes)<dayCount:
                dayIndex = day+counter
                if dayIndex in tickerData and dayIndex not in notIncludedDays:
                    activeDayCounter += 1
                    dayData = tickerData[dayIndex]
                    nextDaySeriesIndexes.append(dayData)
                    futureDayOpenPrice = dayData["ticker"][0]
                    futureDayHighPrice = dayData["ticker"][2]
                    futureDayClosePrice = dayData["ticker"][3]
                    deltaOpen = futureDayOpenPrice - refPrice
                    deltaHigh = futureDayHighPrice - refPrice
                    deltaClose = futureDayClosePrice - refPrice

                    percentOpen = (deltaOpen/refPrice) * 100
                    percentHigh = (deltaHigh/refPrice) * 100
                    percentLow = (deltaClose/refPrice) * 100

                    dayDiff = counter
                    outlookDay = currentDay + datetime.timedelta(days=(dayDiff))
                    weekDay = outlookDay.weekday()
                    if abs(percentOpen) > abs(percentHigh):
                        if abs(percentOpen) > highestDelta:
                            highestDelta = int(abs(percentOpen))
                            isNegative = percentOpen < 0
                    else:
                        if abs(percentHigh) > highestDelta:
                            highestDelta = int(abs(percentHigh))
                            isNegative = percentHigh < 0

                    if percentOpen > maxPositive:
                        maxPositive = percentOpen
                    if percentHigh > maxPositive:
                        maxPositive = percentHigh

                    if percentOpen < maxNegative:
                        maxNegative = percentOpen
                    if percentLow < maxNegative:
                        maxNegative = percentLow

                    ignoreDay = False
                    nextDaySeriesChanges.append([percentOpen, percentHigh, dayDiff, weekDay, percentLow, dayIndex])
                counter += 1

            if not ignoreDay:
                retroDayData = getRetroDayTrainingData(config, tickerData, symbolIndex, dayOfPrediction)
                if retroDayData is not None:
                    featureLen = retroDayData["featureLengthPerRetroDay"]
                    precedingNintyDays = retroDayData["precedingDays"]
                    allRetroDayIndexes = retroDayData["retroDays"]
                    tickerFeaturesPerDay = retroDayData["tickerFeaturesPerDay"]
                    deltaLimit = config.percentageDeltaChange
                    maxDelta = 1 if maxPositive > deltaLimit else 0
                    trainingDays.add(day)
                    retValue[day] = {
                        "day": day,
                        "percentageLimit": str(deltaLimit) + "%",
                        "maxDelta": maxDelta,
                        "retroDays": allRetroDayIndexes,
                        "trainingDays": trainingDays,
                        "nextDaySeriesChanges": nextDaySeriesChanges,
                        "tickerData": nextDaySeriesIndexes,
                        "precedingDays": precedingNintyDays,
                        "featureLengthPerRetroDay": featureLen,
                        "symbolIndex": symbolIndex,
                        "tickerFeaturesPerDay": tickerFeaturesPerDay
                    }
        currentDayIndex += 1
    return retValue


def slicePrecedingDaysToStandardLength(precedingNintyDays, tickerFeaturesPerDay, dayCountForFeatures):
    desiredNumberOfRetroDaysForAnalysis = int(0.6667 * dayCountForFeatures) #We want to have at least two third of the count of the calendar days available as stock days
    retValue = None
    if tickerFeaturesPerDay > 0:
        serializedDayFeatureLimit = desiredNumberOfRetroDaysForAnalysis * tickerFeaturesPerDay
        if len(precedingNintyDays) > serializedDayFeatureLimit:
            precedingNintyDayCount = len(precedingNintyDays)
            precedingNintyDays = precedingNintyDays[(precedingNintyDayCount - serializedDayFeatureLimit):precedingNintyDayCount]
            retValue = precedingNintyDays

    return retValue


def convertTickerForPrediction(tickerData):
    symbolData = []
    symbolKeys = list(tickerData.keys())
    random.shuffle(symbolKeys)
    featureLengthPerRetroDay = None
    for symbolKey in symbolKeys:
        dictOfDaysToPreceedingData = tickerData[symbolKey]
        for targetPredictionDayIndex in dictOfDaysToPreceedingData:
            precedingDays = dictOfDaysToPreceedingData[targetPredictionDayIndex]["precedingDays"]
            symbolIndex = dictOfDaysToPreceedingData[targetPredictionDayIndex]["symbolIndex"]
            symbolAndDayData = {
                'targetPredictionDayIndex' : targetPredictionDayIndex, 
                'symbolIndex': symbolIndex
            }
            # precedingDays.append(symbolAndDayData)  # appending so can be removed in function reshapeData. To be used for assessing qualit of prediction
            precedingDaysData = {
                "precedingDays": precedingDays,
                "metaData":symbolAndDayData
            }
            ignoreFeatureCount = 1
            currentFeatureLengthPerRetroDay = dictOfDaysToPreceedingData[targetPredictionDayIndex]["featureLengthPerRetroDay"]
            if featureLengthPerRetroDay is None:
                featureLengthPerRetroDay = currentFeatureLengthPerRetroDay
            
            if featureLengthPerRetroDay != currentFeatureLengthPerRetroDay:
                raise NameError('It reeks, It reeks')


            symbolData.append(precedingDaysData)
    retValue = {
        'featureLengthPerRetroDay': featureLengthPerRetroDay,
        'symbolData': symbolData
    }
    return retValue


def convertForTraining(tickerData, testRatio, ignoreClassImbalance = False):
    resultToData = {}
    retValue = {}
    featureLengthPerRetroDay = None
    ignoreFeatureCount = None
    symbolKeys = list(tickerData.keys())
    keyLength =len(symbolKeys)
    print ("hey length is "+ str(keyLength))
    random.shuffle(symbolKeys)
    for symbolKey in symbolKeys:
        dictOfDaysToPreceedingData = tickerData[symbolKey]
        
        for targetPredictionDayIndex in dictOfDaysToPreceedingData:
            precedingDays = dictOfDaysToPreceedingData[targetPredictionDayIndex]["precedingDays"]
            symbolIndex = dictOfDaysToPreceedingData[targetPredictionDayIndex]["symbolIndex"]
            # dayDeltas = dictOfDaysToPreceedingData[targetPredictionDayIndex]["featureLengthPerRetroDay"]
            nextDaySeriesChanges= dictOfDaysToPreceedingData[targetPredictionDayIndex]["nextDaySeriesChanges"]
            result = dictOfDaysToPreceedingData[targetPredictionDayIndex]["maxDelta"]
            percentageLimit = dictOfDaysToPreceedingData[targetPredictionDayIndex]["percentageLimit"]
            symbolAndDayData = {
                'targetPredictionDayIndex' : targetPredictionDayIndex, 
                'symbolIndex': symbolIndex,
                'nextDaySeriesChanges': nextDaySeriesChanges,
                "maxDelta": result,
                "percentageLimit": percentageLimit
            }
            # precedingDays.append(symbolAndDayData)  # appending so can be removed in function reshapeData. To be used for assessing qualit of prediction
            precedingDaysData = {
                "precedingDays": precedingDays,
                "metaData":symbolAndDayData
            }
            ignoreFeatureCount = 1
            currentFeatureLengthPerRetroDay = dictOfDaysToPreceedingData[targetPredictionDayIndex]["featureLengthPerRetroDay"]
            if featureLengthPerRetroDay is None:
                featureLengthPerRetroDay = currentFeatureLengthPerRetroDay
            
            if featureLengthPerRetroDay != currentFeatureLengthPerRetroDay:
                raise NameError('It reeks, It reeks')

            if result in resultToData:
                resultToData[result].append(precedingDaysData)
            else:
                collection = []
                collection.append(precedingDaysData)
                resultToData[result] = collection

    ##### section tries to create a 50/50 split in the data if its schewed
    
    minCount = None
    keyWithMinCount = None
    for key in resultToData:
        allFeatures = resultToData[key]
        random.shuffle(allFeatures)
        count = len(resultToData[key])
        if minCount is None or count < minCount:
            minCount = count
            keyWithMinCount = key

    restOfSchewedCollection = []
    schewedKey = None
    
    if not ignoreClassImbalance:
        for key in resultToData:
            if key != keyWithMinCount:
                restOfSchewedCollection = resultToData[key][minCount:]
                schewedKey = key
            resultToData[key] = resultToData[key][:minCount]
    ### End of section removing schewed data
    percentageDiff = []
    for key in resultToData.keys():
        percentageDiff.append(key)
    percentageDiff.sort()


    percentToIndex ={}
    count = 0
    for diff in percentageDiff:
        percentToIndex[diff] = count
        count +=1

    testData = []
    trainData = []
    trainResult = []
    testResult = []
    for result in resultToData:
        allData = resultToData[result]
        totalCount =  len(allData)
        testCount = round(testRatio * totalCount)

        indexes = list(range(totalCount))
        random.shuffle(indexes)

        for index in indexes:
            dataSeries = allData[index]
            if testCount > 0:
                testCount -=1
                testData.append(dataSeries)
                testResult.append(result)
            else:
                trainData.append(dataSeries)
                trainResult.append(result)


    testDataCount = len(testData)
    trainDataCount = len(trainData)

    if (testDataCount == 0 and testRatio != 0 and trainDataCount > 1):
        return convertForTraining(tickerData, testRatio, True)
    
    if (trainDataCount == 0 and testRatio != 1 and testDataCount > 1):
        return convertForTraining(tickerData, testRatio, True)


    if restOfSchewedCollection is not None and len(restOfSchewedCollection) > 0:
        lenOfSchewedData = len(restOfSchewedCollection)
        scheduedKeys = [schewedKey] * lenOfSchewedData

    
    #rnadomizes order of results so we don't have sequential same results so the preceding logic ends up with the resul [0,0,0,0,0,0,1,1,1,1,1,1] and this mixes it up
    for i in range(trainDataCount):
        index = random.randint(0,trainDataCount - 1)
        trainHolder = trainData[i]
        resultHolder = trainResult[i]
        
        trainData[i] = trainData[index]
        trainResult[i] = trainResult[index]
        
        trainData[index] = trainHolder
        trainResult[index] = resultHolder

    for i in range(testDataCount):
        index = random.randint(0,testDataCount - 1)
        testHolder = testData[i]
        testResultHolder = testResult[i]
        
        testData[i] = testData[index]
        testResult[i] = testResult[index]
        
        testData[index] = testHolder
        testResult[index] = testResultHolder

    
    
    retValue = {
        'trainX': trainData,
        'trainY': trainResult,
        'testY': testResult,
        'testX': testData,
        'featureLengthPerRetroDay': featureLengthPerRetroDay,
        'ignoreFeatureCount': ignoreFeatureCount,
        'schewData': None
    }

    if restOfSchewedCollection is not None and len(restOfSchewedCollection) > 0:
        retValue['schewData'] =  {'data': restOfSchewedCollection, 'key':scheduedKeys}
    return retValue


def reshapeData(xs, ys, featureLengthPerRetroDay):
    reformatedXs = [paramFeatures["precedingDays"] for paramFeatures in xs]
    symbolAndFeatures = [paramFeatures["metaData"] for paramFeatures in xs]
    combinedFeaturesPerDay = len(reformatedXs[0])
    numberOfDays = combinedFeaturesPerDay/featureLengthPerRetroDay
    numberOfDaysAsInt = int(numberOfDays) # the number of retro days 

    dataCount = len(reformatedXs)
    reshapedX = array(reformatedXs)
    reshapedX = reshapedX.reshape(dataCount, numberOfDaysAsInt, featureLengthPerRetroDay)
    reshapedX = reshapedX.tolist()
    return {
        'x': reshapedX,
        'y': ys,
        'symbolAndFeatures': symbolAndFeatures
    }


def buildPredictionModel(config:WeatherManPredictionConfig, trainData, trainResult, testData, testResult, featureLengthPerRetroDay, schewedData = None, symbolToIndex = None):
    combinedFeaturesPerDay = len(trainData[0]["precedingDays"])
    numberOfDays = combinedFeaturesPerDay/featureLengthPerRetroDay
    numberOfDaysAsInt = int(numberOfDays) # the number of retro days 

    trainDataCount = len(trainData)
    print("We're training with "+str(trainDataCount) +" data points")
    

    reshaped = reshapeData(trainData, trainResult, featureLengthPerRetroDay)
    trainDataReshaped = reshaped['x']
    trainResultReshaped = reshaped['y']
    metaData = reshaped['symbolAndFeatures']
    optionCount = 2

    validationData = None
    if schewedData is not None:
        extraFeaturesData = schewedData[0]
        extraResults = schewedData[1]
        reshapedResults = reshapeData(extraFeaturesData, extraResults, featureLengthPerRetroDay)
        validationData = (reshapedResults['x'], reshapedResults['y'])

    ###### Model creation 
    model = tf.keras.Sequential()
    model.add(layers.LSTM(256, input_shape =(numberOfDaysAsInt,featureLengthPerRetroDay), return_sequences=False, implementation=2))
    model.add(layers.Dropout(config.dropout))
    model.add(layers.Dense(256, activation='relu'),)
    model.add(layers.Dense(optionCount, activation='softmax'))

    numberOfEpochs = config.epochCount
    learningRate = 0.001
    optimizer = tf.compat.v1.train.AdamOptimizer(
        learning_rate=learningRate, beta1=0.9, beta2=0.999, epsilon=1e-08, use_locking=False,
        name='Adam'
    )

    model.compile(optimizer=optimizer,
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])
    
    print(model.summary())
    history = model.fit(trainDataReshaped, trainResultReshaped, 
        validation_data= validationData,
        epochs=numberOfEpochs,
        # verbose=2
        )
    retValue = (model, None, None)
    if testData is not None and testResult is not None:
        testDataCount = len(testData)
        print("We're testing with "+str(testDataCount) +" data points")
        reshaped = reshapeData(testData, testResult, featureLengthPerRetroDay)
        testDataReshaped = reshaped['x']
        testResultReshaped = reshaped['y']
        test_loss, test_acc = model.evaluate(testDataReshaped,  testResultReshaped, verbose=2)
        print('\nTest accuracy:', test_acc)
        retValue = (model, test_loss, test_acc)
        prediction = model.predict(testDataReshaped, verbose=2)
        prediction_probabilities = list(prediction)

        prediction = model.predict_classes(testDataReshaped, verbose=2)
        predictionArr = prediction.tolist()
        oneErrorRate(predictionArr, testResultReshaped, testData, prediction_probabilities, symbolToIndex,
            # True
        )
    return retValue

def pickStockFromProbabilities(predictionProbability, numberOfStockForProbability = 5, stockPerDay = 2, probabilityRetryCount = 1000, threshold = 0.95):
    orderedByBestProbability = sorted(predictionProbability, key=lambda Probabs: (Probabs["wrongProbability"]))
    bestFiveStocks = orderedByBestProbability[:numberOfStockForProbability]
    minThresholdStocks = [stockData for stockData in bestFiveStocks if stockData["rightProbability"] > threshold ]
    
    retValue = []
    if len(minThresholdStocks) > 1:
        poulatedByRandomness = []
        listGenCounter = 0
        while listGenCounter < len(minThresholdStocks):
            poulatedByRandomness.append({
                "counter": 0,
                "index": listGenCounter
            })
            listGenCounter+=1

        indexLimit = len(minThresholdStocks) - 1
        
        retryCounter = 0
        while retryCounter < probabilityRetryCount:
            ranDomIndex = random.randint(0, indexLimit)
            poulatedByRandomness[ranDomIndex]["counter"] += 1
            retryCounter +=1

        sortedRandomIndex = sorted(poulatedByRandomness, key=lambda entry: entry["counter"], reverse=True)
        selectedRandomIndexes = sortedRandomIndex[:stockPerDay]
        retValue = [minThresholdStocks[stockIndex['index']] for stockIndex in selectedRandomIndexes]

    else:
        if len(minThresholdStocks) == 0:
            return retValue
        else:
            retValue.append(minThresholdStocks[0])
    
    return retValue
   
def getPredictions(config:WeatherManPredictionConfig, model, testData, testResults, featureLengthPerRetroDay, indexToSymbol, printSomeThing = False):
    reshaped = reshapeData(testData, testResults, featureLengthPerRetroDay)
    testDataReshaped = reshaped['x']

    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()

    retValue = processPredictions(predictionArr, prediction_probabilities, testData, testResults, indexToSymbol)
    return retValue

def assessPredictions(config:WeatherManPredictionConfig, model, testData, testResults, featureLengthPerRetroDay, indexToSymbol, stockPerDay = 2, printSomeThing = False):
    reshaped = reshapeData(testData, testResults, featureLengthPerRetroDay)
    testDataReshaped = reshaped['x']

    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()

    predictionProcessed = processPredictions(predictionArr, prediction_probabilities, testData, testResults, indexToSymbol)
    

    totalCorrectlyPredicted = 0
    totalOnesPredicted = 0


    willBuyTHeFollowing = []

    if 1 in predictionProcessed:
        marketUpPredictions = predictionProcessed[1]
        for predictionDayIndex in marketUpPredictions:
            predictionDayStockPredictions = marketUpPredictions[predictionDayIndex]
            # for predictionDayIndex in predictionDayStockPredictions:
            # allStockPredictions = predictionDayStockPredictions[predictionDayIndex]
            selectedStocks = pickStockFromProbabilities(predictionDayStockPredictions, stockPerDay=stockPerDay, threshold=config.threshold)
            willBuyTHeFollowing.extend(selectedStocks)
            for selectedStock in selectedStocks:
                totalOnesPredicted += 1
                if selectedStock["result"] == 1:
                    totalCorrectlyPredicted += 1
    
    if(printSomeThing or (totalOnesPredicted != totalCorrectlyPredicted)):
        print("You should bid on the following stock")
        print(str(willBuyTHeFollowing))
        print("\n")
    retValue = {
        'correctPredictions': totalCorrectlyPredicted,
        'totalOnesPredicted': totalOnesPredicted,
        'toBeBoughtStocks': willBuyTHeFollowing
    }

    return retValue


    


def oneErrorRate (prediction, result, testData, prediction_probabilities = None, symbolToIndex = None, printResult = False):
    countLimit = len(prediction)
    index = 0
    onePredictionCount = 0
    correctOneCountPrediction = 0
    SuccessfullPredictions = []
    FailedPredictions = []
    combinePredictions = []
    onlyOneCounts = []
    
    while index < countLimit:
        resultValue = result[index]
        testDatum = testData[index]
        metadata = testDatum["metaData"]
        predictionValue = prediction[index]
        probs = None
        predictionAndIndex = None
        
        if prediction_probabilities is not None:
            probs = prediction_probabilities[index]
            predictionAndIndex = list(probs)
            stockSymbol = metadata["symbolIndex"]
            if symbolToIndex is not None:
                dayIndex = metadata['targetPredictionDayIndex']
                dayAsTime = timeFromDayIndex(dayIndex)
                predictionAndIndex.append(stockSymbol)
                predictionAndIndex.append(dayIndex)
                predictionAndIndex.append(str(dayAsTime))
            combinePredictions.append(predictionAndIndex)
            

        if predictionValue == 1:
            onePredictionCount+=1
            onlyOneCounts.append(predictionAndIndex)
            if resultValue == 1:
                correctOneCountPrediction += 1
                if probs is not None:
                    SuccessfullPredictions.append(probs.tolist())
                    predictionAndIndex.extend([index, True])
            else:
                if probs is not None:
                    FailedPredictions.append(probs.tolist())
                    predictionAndIndex.extend([index, False])
        index+=1

    if onePredictionCount > correctOneCountPrediction:
        print ("Correct one prediction ratio "+ str( ((correctOneCountPrediction )/onePredictionCount) * 100) + "%")
    
    sortedOnlyOneCounts = sorted(onlyOneCounts, key=lambda Probabs: (Probabs[3], Probabs[0]))

    if printResult:
        print("Sorted CombinedPredictions count " + str(sortedOnlyOneCounts))



def processPredictions(predictions, predictionProbabilities, testData, testResults, indexToSymbol):
    OnePredicitons = {} # this holds a dayIndex -> ([topFiveProbabilityStockData], set(winningStocks))
    ZeroPredicitons = {}
    if (predictions is not None and predictionProbabilities is not None
        and testData is not None and testResults is not None
        and len(testResults) == len(predictionProbabilities) == len(predictions)):
        index = 0
        countLimit = len(predictions)
        while index < countLimit:
            testDatum = testData[index]
            metadata = testDatum["metaData"]
            predictionDayIndex = metadata['targetPredictionDayIndex']
            predictionProbability = predictionProbabilities[index]
            stockSymbol = metadata["symbolIndex"]
            prediction = predictions[index]
            testResult = testResults[index]
            if prediction == 1:
                predictionDayStockPredictions = []
                if predictionDayIndex in OnePredicitons:
                    predictionDayStockPredictions = OnePredicitons[predictionDayIndex]
                else:
                    OnePredicitons[predictionDayIndex] = predictionDayStockPredictions
                predictionDict = {
                    "wrongProbability": predictionProbability[0],
                    "rightProbability": predictionProbability[1],
                    "symbol": stockSymbol,
                    "result": testResult,
                    "predictionDay": str(timeFromDayIndex(predictionDayIndex)),
                    "predictionDayIndex": predictionDayIndex,
                    "prediction": prediction
                }
                predictionDayStockPredictions.append(predictionDict)
            else:
                predictionDayStockPredictions = []
                if predictionDayIndex in ZeroPredicitons:
                    predictionDayStockPredictions = ZeroPredicitons[predictionDayIndex]
                else:
                    ZeroPredicitons[predictionDayIndex] = predictionDayStockPredictions
                predictionDict = {
                    "wrongProbability": predictionProbability[0],
                    "rightProbability": predictionProbability[1],
                    "symbol": stockSymbol,
                    "result": testResult,
                    "predictionDay": str(timeFromDayIndex(predictionDayIndex)),
                    "predictionDayIndex": predictionDayIndex,
                    "prediction": prediction
                }
                predictionDayStockPredictions.append(predictionDict)
            index+=1
    
    retValue = {
        0: ZeroPredicitons,
        1: OnePredicitons
    }

    return retValue
        


def predict(config:WeatherManPredictionConfig, model, indexToSymbol, testData, featureLengthPerRetroDay):
    reshaped = reshapeData(testData, None, featureLengthPerRetroDay)
    testDataReshaped = reshaped['x']

    stockSymbolFeatures = reshaped['symbolAndFeatures']
    
    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()

    predictionLength = len(prediction_probabilities)
    predictionResultMapping = {
        0: [],
        1: []
    }
    for i in range(predictionLength):
        predictionResult = predictionArr[i]
        predictionProbability = prediction_probabilities[i]
        stockSymbol = stockSymbolFeatures[i]
        predictionDict = {
                    "wrongProbability": predictionProbability[0],
                    "rightProbability": predictionProbability[1],
                    "symbol": stockSymbol['symbolIndex'],
                    "prediction": predictionResult
                }
        predictionResultMapping[predictionResult].append(predictionDict)

    onePredictions = predictionResultMapping[1]
    retValue = pickStockFromProbabilities(onePredictions, stockPerDay=config.stockPerDay, threshold=config.threshold)
    return retValue
    


def daysToDictionary(dayIndexes, mappings):
    retValue = {}
    for dayIndex in dayIndexes:
        retValue[dayIndex] = mappings[dayIndex]
    return retValue

def loadAllSymbolTickerDataIntoMemory(tickerSymbols):
    retValue = {}
    for symbol in tickerSymbols:
        tickerData = load_time_series_daily(symbol)
        retValue[symbol] = tickerData
    return retValue

def getAllTrainingPieces(config:WeatherManPredictionConfig, tickerSymbols):
    allSymbolsToTickerData = loadAllSymbolTickerDataIntoMemory(tickerSymbols)
    bounds = {
        "min":None,
        "max":None,
    }

    dayIndexes = set()
    dataIndexToSymbol = {}
    symbolCounter = 0
    for entry in allSymbolsToTickerData:
        currentMin = bounds["min"]
        currentMax = bounds["max"]
        symbolInfo = allSymbolsToTickerData[entry]
        stockDayIndexMin = symbolInfo["dayBounds"]["min"]
        stockDayIndexMax = symbolInfo["dayBounds"]["max"]
        symbolDayIndexes = symbolInfo["allDayIndexes"]
        dataIndexToSymbol[entry] = symbolCounter
        for dayIndex in symbolDayIndexes:
            dayIndexes.add(dayIndex)


        if currentMin is None or stockDayIndexMin < currentMin:
            currentMin = stockDayIndexMin
            bounds["min"] = currentMin

        if currentMax is None or currentMax < stockDayIndexMax:
            currentMax = stockDayIndexMax
            bounds["max"] = currentMax
        symbolCounter += 1
    
    retValue = {
        "bounds": bounds,
        "allSymbolsToTickerData": allSymbolsToTickerData,
        "dataIndexToSymbol": dataIndexToSymbol,
        "dayIndexes": dayIndexes
    }

    return retValue
    
    # retrievedMinDayIndex = bounds["min"]
    # retrievedMaxDayIndex = bounds["max"]
    # outlookDayDifference = outlookDayLimit
    # retryCount = 2
    # maxTestableIndex = retrievedMaxDayIndex
    # while outlookDayDifference >0 and retryCount > 0:
    #     if maxTestableIndex in dayIndexes:
    #         maxTestableIndex -= 1
    #         outlookDayDifference -= 1
    #     else:
    #         retryCount -= 1


def dayIntervalConfidenceTest(boundStartTime, boundEndTime, tickerSymbols, config:WeatherManPredictionConfig):
    if( boundEndTime is None):
        boundEndTime = datetime.datetime.now()
    entryDayStartIndex = dayIndexFromStart(boundStartTime)
    entryDayEndIndex = dayIndexFromStart(boundEndTime)
    outlookDayLimit = config.numberOfOutlookDays
    
    parameters = getAllTrainingPieces(config, tickerSymbols)


    bounds = parameters["bounds"]
    dayIndexes = parameters["dayIndexes"]
    allSymbolsToTickerData = parameters["allSymbolsToTickerData"]
    dataIndexToSymbol = parameters["dataIndexToSymbol"]
    retrievedMinDayIndex = bounds["min"]
    retrievedMaxDayIndex = bounds["max"]
    outlookDayDifference = outlookDayLimit
    retryCount = 2
    maxTestableIndex = retrievedMaxDayIndex
    while outlookDayDifference >0 and retryCount > 0:
        if maxTestableIndex in dayIndexes:
            maxTestableIndex -= 1
            outlookDayDifference -= 1
        else:
            retryCount -= 1
    
    loopMaxIndex = maxTestableIndex
    loopMinIndex = retrievedMinDayIndex
    if entryDayEndIndex < loopMaxIndex:
        loopMaxIndex = entryDayEndIndex

    if  entryDayStartIndex > loopMinIndex:
        loopMinIndex = entryDayStartIndex

    numberOfDaysForTraining = config.numberOfDaysForTraining
    trainingDayStartIndex = loopMinIndex
    trainingDayEndIndex = trainingDayStartIndex + numberOfDaysForTraining
    totalCorrectOnesPrediction = 0
    totalOnesPrediction = 0
    predictionDayCounter = 0
    totalDayCounter = 0
    alreadyPredictedDays = set()
    rebuildModel = False
    foundPredictionDay = False
    numberOfPossiblePredictions = 0
    numberOfActivePredictions = 0
    sumOfPredictionSuccessRatio = 0
    eachdayAssessment = {}
    while trainingDayEndIndex <= loopMaxIndex:
        trainingStartTime = timeFromDayIndex(trainingDayStartIndex)
        trainingEndTime = timeFromDayIndex(trainingDayEndIndex)
        print("Looping again time frame "+str(trainingStartTime) +" - " + str(trainingEndTime))
        symbolToDayData = {}
        model = None
        dayCountBeforeModelRebuild = config.numberOfDaysBeforeRetrainingModel
        dayBeforeModelrebuildCounter = 0
        predictionDayStartDayIndex = trainingDayEndIndex + config.numberOfOutlookDays
        predictionDayEndDayIndex = predictionDayStartDayIndex+1
        predictionDayCounter = 0
        rebuildModel = True
        foundPredictionDay = False
        while dayBeforeModelrebuildCounter < dayCountBeforeModelRebuild and predictionDayStartDayIndex <= loopMaxIndex:
            if rebuildModel:
                modelResults = getModels(config, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime)
                models = [modelResult['model']  for modelResult in modelResults]
                rebuildModel = False
            if predictionDayStartDayIndex in dayIndexes and  predictionDayStartDayIndex not in alreadyPredictedDays:
                totalDayCounter+=1
                symbolToDayData = {}
                predictionDayStartTime = timeFromDayIndex(predictionDayStartDayIndex)
                predictionDayEndTime = timeFromDayIndex(predictionDayEndDayIndex)
                for symbol in allSymbolsToTickerData:
                    if symbol not in symbolToDayData:
                        tickerData = allSymbolsToTickerData[symbol]["symbolData"]
                        stockDataDayCount = len(tickerData)
                        if stockDataDayCount > numberOfDaysForTraining:
                            outlookResult = getDayOutlook(config, tickerData, predictionDayStartTime, predictionDayEndTime, symbolIndex = symbol)
                            symbolToDayData[symbol] = outlookResult
                        else:
                            print("Insufficient data for "+ symbol+"\nTotal days is : "+str(numberOfDaysForTraining)+"\nStock Days is :"+str(stockDataDayCount))
                
                # dataFormated = convertForTraining(symbolToDayData,0, True)
                # trainData = dataFormated['trainX']
                # trainResult = dataFormated['trainY']
                # featureDayLength = dataFormated['featureLengthPerRetroDay']
                # modelAssessment = assessPredictions(config, model, trainData, trainResult, featureDayLength, dataIndexToSymbol, config.stockPerDay)
                modelAssessment = multipleModelAssessment(config, models, symbolToDayData, dataIndexToSymbol, config.stockPerDay, True)
                totalOnesPredicted =modelAssessment['totalOnesPredicted']
                correctPredictions = modelAssessment['correctPredictions']
                numberOfPossiblePredictions +=1
                
                totalOnesPrediction += totalOnesPredicted
                totalCorrectOnesPrediction += correctPredictions
                print("Model is for the time frame "+str(trainingStartTime) +" - " + str(trainingEndTime))
                if totalOnesPredicted != 0:
                    numberOfActivePredictions +=1
                    predictionsResults = [] 
                    if predictionDayStartDayIndex in eachdayAssessment:
                        predictionsResults = eachdayAssessment[predictionDayStartDayIndex]
                    else:
                        eachdayAssessment[predictionDayStartDayIndex] = predictionsResults
                    predictionsResults.append(modelAssessment)
                    dayFinalAccuracyRatio = (correctPredictions/totalOnesPredicted )
                    sumOfPredictionSuccessRatio+=dayFinalAccuracyRatio
                    dayFinalAccuracy =  dayFinalAccuracyRatio * 100
                    print("Bidding accuracy for Day "+str(predictionDayStartTime)+" is "+str(dayFinalAccuracy))

                if totalOnesPrediction != 0:
                    soFarAccuracy = (totalCorrectOnesPrediction/totalOnesPrediction ) * 100
                    print("Total accuracy sofar "+str(soFarAccuracy))
                print("processed "+str(totalDayCounter)+" days "+str(predictionDayStartTime))
                alreadyPredictedDays.add(predictionDayStartDayIndex)
                dayBeforeModelrebuildCounter+=1
            foundPredictionDay = True
            predictionDayCounter +=1
            predictionDayStartDayIndex += 1
            predictionDayEndDayIndex += 1
            
        if(foundPredictionDay) :
            trainingDayStartIndex += (predictionDayCounter)
            trainingDayEndIndex += (predictionDayCounter)
        else:
            trainingDayStartIndex += 1
            trainingDayEndIndex += 1
    
    print("EACH DAY ASSESSMENT")
    print(eachdayAssessment)
    config.printMe()

    print("Complete time frame is "+str(timeFromDayIndex(trainingDayStartIndex))+" to "+str(timeFromDayIndex(trainingDayEndIndex)))
    if totalOnesPrediction != 0:
        finalAccuracy = (totalCorrectOnesPrediction/totalOnesPrediction ) * 100
        print("Bidding accuracy is "+str(finalAccuracy))
        activePredictionRatio = (numberOfActivePredictions/numberOfPossiblePredictions) * 100
        print("There was a prediction "+ str(activePredictionRatio) + "pct of the days")
    else:
        print("Nothing to buy")


def getModels(config:WeatherManPredictionConfig, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime):
    models = []
    modelRebuildCounter = 0
    symbolToDayData = {}
    numberOfDaysForTraining = config.numberOfDaysForTraining
    symbolReadStart = datetime.datetime.now()
    for symbol in allSymbolsToTickerData:
        if symbol not in symbolToDayData:
            tickerData = allSymbolsToTickerData[symbol]["symbolData"]
            print("symbol is "+ str(symbol))
            stockDataDayCount = len(tickerData)
            
            if stockDataDayCount > numberOfDaysForTraining:
                outlookResult = getDayOutlook(config, tickerData, trainingStartTime, trainingEndTime, symbolIndex = symbol)
                symbolToDayData[symbol] = outlookResult
            else:
                print("Insufficient data for "+ symbol+"\nTotal days is : "+str(numberOfDaysForTraining)+"\nStock Days is :"+str(stockDataDayCount))
    
    symbolReadEnd = datetime.datetime.now()

    timeSpan = symbolReadEnd - symbolReadStart
    print("symbol read took "+ str(timeSpan.total_seconds()) +"s")
    while modelRebuildCounter < config.modelRebuildCount:
        modelInfo = getModel(config, symbolToDayData, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime)
        if(modelInfo is not None):
            models.append(modelInfo)
        modelRebuildCounter += 1
    
    return models


def getBestModel(config:WeatherManPredictionConfig, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime):
    retValue = None
    models = []
    modelRebuildCounter = 0
    symbolToDayData = {}
    numberOfDaysForTraining = config.numberOfDaysForTraining
    symbolReadStart = datetime.datetime.now()
    for symbol in allSymbolsToTickerData:
        if symbol not in symbolToDayData:
            tickerData = allSymbolsToTickerData[symbol]["symbolData"]
            print("symbol is "+ str(symbol))
            stockDataDayCount = len(tickerData)
            
            if stockDataDayCount > numberOfDaysForTraining:
                outlookResult = getDayOutlook(config, tickerData, trainingStartTime, trainingEndTime, symbolIndex = symbol)
                symbolToDayData[symbol] = outlookResult
            else:
                print("Insufficient data for "+ symbol+"\nTotal days is : "+str(numberOfDaysForTraining)+"\nStock Days is :"+str(stockDataDayCount))
    
    symbolReadEnd = datetime.datetime.now()

    timeSpan = symbolReadEnd - symbolReadStart
    print("symbol read took "+ str(timeSpan.total_seconds()) +"s")
    while modelRebuildCounter < config.modelRebuildCount:
        modelInfo = getModel(config, symbolToDayData, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime)
        if(modelInfo is not None):
            models.append(modelInfo)
        modelRebuildCounter += 1
    
    if len(models) > 0:
        retValue = sorted(models, key=lambda eachModel: eachModel["test_acc"], reverse=True)[0]
    
    return retValue


def multipleModelAssessment(config:WeatherManPredictionConfig, models, symbolToDayData, dataIndexToSymbol, stockPerDay, printSomeThing = False):
    
    symbolToPredictions = {}
    countToSymbolPredictions = {}
    for model in models:
        dataFormated = convertForTraining(symbolToDayData,0, True)
        trainData = dataFormated['trainX']
        trainResult = dataFormated['trainY']
        featureDayLength = dataFormated['featureLengthPerRetroDay']
        modelPredictions = getPredictions(config, model, trainData, trainResult, featureDayLength, dataIndexToSymbol, printSomeThing)
        

        if 1 in modelPredictions:
            marketUpPredictions = modelPredictions[1]
            for predictionDayIndex in marketUpPredictions:
                predictionDayStockPredictions = marketUpPredictions[predictionDayIndex]
                selectedStocks = pickStockFromProbabilities(predictionDayStockPredictions, stockPerDay=stockPerDay, threshold=config.threshold)
                for selectedStock in selectedStocks:
                    symbol = selectedStock["symbol"]
                    if symbol in symbolToPredictions:
                        modelPredictions = symbolToPredictions[symbol]
                    else:
                        modelPredictions = {
                            'prediction': [],
                            'lowestProbability': 2,
                        }
                        symbolToPredictions[symbol] = modelPredictions

                    modelPredictions['prediction'].append(selectedStock)
                    if(selectedStock['wrongProbability'] < modelPredictions['lowestProbability']):
                        modelPredictions['lowestProbability'] = selectedStock['wrongProbability']
        
    for symbol in symbolToPredictions:
        stockPredictions = symbolToPredictions[symbol]
        predictionCount = len(stockPredictions['prediction'])
        if predictionCount in countToSymbolPredictions:
            countToSymbolPredictions[predictionCount].append(stockPredictions)
        else:
            countToSymbolPredictions[predictionCount] = [stockPredictions]

    countKeys = list(countToSymbolPredictions.keys())
    highCountKeys = sorted(countKeys, reverse=True)
    allPredictions = []
    for countKey in highCountKeys:
        predictions = highCountKeys[countKey]
        sortedPredictions = sorted(predictions, key=lambda prediction: prediction['wrongProbability'])
        allPredictions.extend(sortedPredictions)

    finalPredictions = allPredictions[:stockPerDay]
    for selectedStock in finalPredictions:
        totalOnesPredicted += 1
        if selectedStock["result"] == 1:
            totalCorrectlyPredicted += 1
    
    willBuyTHeFollowing = {}
    if(printSomeThing or (totalOnesPredicted != totalCorrectlyPredicted)):
        print("You should bid on the following stock")
        print(str(willBuyTHeFollowing))
        print("\n")
    retValue = {
        'correctPredictions': totalCorrectlyPredicted,
        'totalOnesPredicted': totalOnesPredicted,
        'toBeBoughtStocks': willBuyTHeFollowing
    }

    return retValue

    

def getModel(config:WeatherManPredictionConfig, symbolToDayData, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTime, trainingEndTime):
    
    retValue = None
    if len(symbolToDayData) > 0:
        trainResult = []
        trainData = []
        testResult = []
        testData = []

        dataFormated = convertForTraining(symbolToDayData, config.testRatio)
        trainData = dataFormated['trainX']
        trainResult =dataFormated['trainY']
        testData = dataFormated['testX']
        testResult = dataFormated['testY']
        featureDayLength = dataFormated['featureLengthPerRetroDay']
        

        (model, test_loss, test_acc) = buildPredictionModel(config, trainData, trainResult, testData, testResult, featureDayLength, (testData, testResult), dataIndexToSymbol)
        retValue = {
            'model': model,
            'test_loss': test_loss,
            'test_acc': test_acc
        }

    return retValue


def getStockSuggestionSymbolToData(config:WeatherManPredictionConfig, allSymbolsToTickerData, predictonDayIndex):
    symbolToDayData = {}
    numberOfDaysForTraining = config.numberOfDaysForTraining
    for symbol in allSymbolsToTickerData:
        if symbol not in symbolToDayData:
            tickerData = allSymbolsToTickerData[symbol]["symbolData"]
            stockDataDayCount = len(tickerData)
            if stockDataDayCount > numberOfDaysForTraining and predictonDayIndex in tickerData:
                symbolPredictionData = {}
                symbolPredictionData[predictonDayIndex] = getRetroDayTrainingData(config, tickerData, symbol, predictonDayIndex)
                outlookResult = symbolPredictionData
                symbolToDayData[symbol] = outlookResult
                print("found "+str(timeFromDayIndex(predictonDayIndex))+" for "+str(symbol))
            else:
                if predictonDayIndex not in tickerData:
                    print("Cannot find "+str(timeFromDayIndex(predictonDayIndex))+" for "+str(symbol))
                else:
                    print("Insufficient data for "+ symbol+"\nTotal days is : "+str(numberOfDaysForTraining)+"\nStock Days is :"+str(stockDataDayCount))
    
    return symbolToDayData
    

def getStocks(tickerSymbols, date=None):
    config = WeatherManPredictionConfig()
    config.epochCount = 200
    config.modelRebuildCount = 3
    currentTime = datetime.datetime.now()
    config.printMe()
    if date is None:
        date = currentTime
    earliestTime = currentTime + datetime.timedelta(days=(-180))
    finalTime = date #+ datetime.timedelta(days=())

    print ("We are about to predict stocks to buy on "+str(finalTime))

    parameters = getAllTrainingPieces(config, tickerSymbols)
    allSymbolsToTickerData = parameters["allSymbolsToTickerData"]
    dataIndexToSymbol = parameters["dataIndexToSymbol"]
    allDayIndexes = parameters["dayIndexes"]

    trainingStartTIme = earliestTime
    trainingEndTime = finalTime + datetime.timedelta(days=(-config.numberOfOutlookDays))
    model = getBestModel(config, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTIme, trainingEndTime)["model"]
    predictionStartTime = finalTime
    retryCountLimit = 4
    retryCount = 0
    predictionDayIndex = dayIndexFromStart(predictionStartTime)

    while predictionDayIndex not in allDayIndexes and retryCount < retryCountLimit:
        predictionDayIndex -= 1
        retryCount += 1
    
    if predictionDayIndex in allDayIndexes:
        symbolToDayData = getStockSuggestionSymbolToData(config, allSymbolsToTickerData, predictionDayIndex)
    
        predictionData = convertTickerForPrediction(symbolToDayData)
        stockData = predictionData['symbolData']
        featureLengthPerRetroDay = predictionData['featureLengthPerRetroDay']
        stockResult = predict(config, model, dataIndexToSymbol, stockData, featureLengthPerRetroDay)
        if(len(stockResult) > 0):
            print ("Done analyzing you should buy the stocks below:")
            print(stockResult)
        else: 
            print ("\n\n\nSorry bro, no stock buying today")
    else:
        print ("Cannot predict stock because the time provided is not within")


def runExec(tickerSymbols = None):
    config = WeatherManPredictionConfig()
    config.iterationNotes = '''Changed how inflection points of preceding day works.
        added inflection points and fixed logincal errors
        retryLimit = dayCount + 2 
        subSetOfTech[51:102]
        retValue = [lowestInflextionPointsFeatures,
                 highestInflextionPointFeatures
                 ]
     '''
    
    # getStocks(tickerSymbols)
    # return
    config.printMe()
    currentTime = datetime.datetime.now()
    
    earliestTime = currentTime + datetime.timedelta(days=(-165))
    finalTime = currentTime  + datetime.timedelta(days=(0))
    confidenceAnalysisStart = datetime.datetime.now()
    print("Analysis is "+str(earliestTime)+" to "+str(finalTime))
    dayIntervalConfidenceTest(earliestTime, finalTime, tickerSymbols, config)
    print("Analysis is "+str(earliestTime)+" to "+str(finalTime))
    confidenceAnalysisEnd = datetime.datetime.now()
    timeSpan = confidenceAnalysisEnd - confidenceAnalysisStart
    print("confidence analysis took "+ str(timeSpan.total_seconds()) +"s")
    config.printMe()

# def runExec(tickerSymbols = None):
#     defaultSymbol = "MMM"
#     config = WeatherManPredictionConfig()
#     currentTime = datetime.datetime.now()
#     years = 0.3
#     daysPerYear = 365
#     totalDays = years * daysPerYear
#     earliestTime = currentTime + datetime.timedelta(days=(-totalDays))
#     finalTime = currentTime + datetime.timedelta(days=(-4))
#     if not tickerSymbols:
#         tickerSymbols = [defaultSymbol]
#     dataIndexToSymbol = {}
#     symbolToDayData = {}
#     symbolCounter = 0
#     for symbol in tickerSymbols:
#         if symbol not in symbolToDayData:
#             tickerData = load_time_series_daily(symbol)
#             print("symbol is "+ str(symbol))
#             stockDataDayCount = len(tickerData)
#             if stockDataDayCount > totalDays:
#                 outlookResult = getDayOutlook(config, tickerData, earliestTime, finalTime, symbolIndex = symbolCounter)
#                 symbolToDayData[symbol] = outlookResult
#                 dataIndexToSymbol[symbolCounter] = symbol
#                 symbolCounter += 1
#             else:
#                 print("Insufficient data for "+ symbol+"\nTotal days is : "+str(totalDays)+"\nStock Days is :"+str(stockDataDayCount))

#     if len(symbolToDayData) > 0:
#         trainResult = []
#         trainData = []
#         allTestResult = []
#         allTestData = []
#         multiTestDayData = []
#         multiTestDayResult = []


#         futureDayCount = config.numberOfDaysBeforeRetrainingModel
#         symbolFeatureLengthPerRetroDay = -3
#         symbolKeys = symbolToDayData.keys()

        

#         print("using the time frame "+str(earliestTime)+ " - "+str(finalTime))
#         print("Predicting "+str(futureDayCount)+ " days into the future")

#         for key in symbolKeys:
#             trainingDays = None
#             for value in symbolToDayData[key].values():
#                 trainingDays = value["trainingDays"]
#                 break
#             allTestPerSymbol = []
#             allResultPerSymbol = []
#             if trainingDays is not None:
#                 orderedTraingDays = sorted(trainingDays)
#                 trainDataDays = orderedTraingDays[:len(orderedTraingDays) - futureDayCount]
#                 testDataDays = orderedTraingDays[(len(orderedTraingDays) - futureDayCount):]
#                 trainSymbolToDayData = {
#                     ""+key+"": daysToDictionary(trainDataDays, symbolToDayData[key])
#                 }
                
#                 testSymbolToDayData = {
#                     ""+key+"": daysToDictionary(testDataDays, symbolToDayData[key])
#                 }

                
#                 dataFormated = convertForTraining(trainSymbolToDayData, 0)
#                 trainResult.extend( dataFormated['trainY'])
#                 trainData.extend(dataFormated['trainX'])
#                 allTestResult.extend(dataFormated['testY'])
#                 allTestData.extend(dataFormated['testX'])

#                 allResultPerSymbol.extend(dataFormated['testY'])
#                 allTestPerSymbol.extend(dataFormated['testX'])

#                 dataFormated = convertForTraining(testSymbolToDayData, 1, True)
#                 trainResult.extend( dataFormated['trainY'])
#                 trainData.extend(dataFormated['trainX'])
#                 allTestResult.extend(dataFormated['testY'])
#                 allTestData.extend(dataFormated['testX'])

#                 allResultPerSymbol.extend(dataFormated['testY'])
#                 allTestPerSymbol.extend(dataFormated['testX'])

#                 featureDayLength = dataFormated['featureLengthPerRetroDay']
#                 symbolFeatureLengthPerRetroDay = featureDayLength
                
#             multiTestDayData.append(allTestPerSymbol)
#             multiTestDayResult.append(allResultPerSymbol)

        
#         (model, test_loss, test_acc) = buildPredictionModel(config, trainData, trainResult, allTestData, allTestResult, symbolFeatureLengthPerRetroDay, (allTestData, allTestResult), dataIndexToSymbol)
        
#         for index in range(len(multiTestDayData)):
#             testDataIter = multiTestDayData[index]
#             testResultIter = multiTestDayResult[index]
#             if(len(testDataIter) > 0):
#                 modelAssessment = assessPredictions(model, testDataIter, testResultIter, symbolFeatureLengthPerRetroDay, dataIndexToSymbol)
#                 print("using the time frame "+str(earliestTime)+ " - "+str(finalTime))
#                 print("Predicting "+str(futureDayCount)+ " days into the future")
#                 totalOnesPredicted =modelAssessment['totalOnesPredicted']
#                 correctPredictions = modelAssessment['correctPredictions']
#                 if totalOnesPredicted != 0:
#                     finalAccuracy = (correctPredictions/totalOnesPredicted ) * 100
#                     print("Bidding accuracy is "+str(finalAccuracy))
#                 else:
#                     print("Nothing to buy")
#     else:
#         print("Could not find data to process")

