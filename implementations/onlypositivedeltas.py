import json
import datetime
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from .multiDayEvaluation import WeatherManPredictionTestConfig 
import matplotlib.pyplot as plt
from numpy import array, transpose

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.loaddataseries import load_time_series_daily

# config = tf.ConfigProto()
# config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
# config.log_device_placement = True  # to log device placement (on which device the operation ran)
#                                     # (nothing gets printed in Jupyter, only if you run it standalone)
# sess = tf.Session(config=config)
# set_session(sess)  # set this TensorFlow session as the default session for Keras


# This works by looking forward into a given number of days from a given day.
# It generates a collecion of all the deltass of the future days high from the a given days opening price
# Any day with delta higher than 'deltaLimit' will be set to some max value
def  precedingDayIndexes(currentDayIndex, dayCount, tickerDictionary):
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



def getPreceedingDayFeatures(dayIndex, timeData):
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

    def sortByHighPrice(x, y):
        return x[maxPriceKey][1] - y[maxPriceKey][1]
    
    def sortByLowPrice(x, y):
        return x[lowPriceKey][1] - y[lowPriceKey][1]
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
    
    inflextionCount = 3
    sortedByHigh =sorted(allvalues, key=lambda highPrice: highPrice[maxPriceKey][1])
    sortedByLow =sorted(allvalues, key=lambda lowPrice: lowPrice[lowPriceKey][1])

    highestInflexionPoints = sortedByHigh[len(sortedByHigh)-inflextionCount:]
    lowestInflextionPoints = sortedByLow[:inflextionCount]
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
        averageDelta = 0
        for inflexionPoint in inflexionPoints:
            inflexionDayIndex = inflexionPoint[0]
            inflexionDayPrice = inflexionPoint[1]
            if dayIndex != inflexionDayIndex:
                dayDiff = dayIndex - inflexionPoint[0] 
                dayDeltas.append(dayDiff)
                diffBetweenDelta = dayDiff - currentDayDiff
                diffBetweenDeltas.append(diffBetweenDelta)
                gradientAvgPriceForDay = (avgPrice - inflexionDayPrice)/dayDiff
                avgPriceGradient.append(gradientAvgPriceForDay)
                gradientLowPriceForDay = (lowestPrice - inflexionDayPrice)/dayDiff
                lowPriceGradient.append(gradientLowPriceForDay)
                gradientHighPriceForDay = (highestPrice - inflexionDayPrice)/dayDiff
                highestPriceGradient.append(gradientHighPriceForDay)

        if len(diffBetweenDeltas) != 0:
            averageDelta = sum(diffBetweenDeltas)/len(diffBetweenDeltas)
        averagePriceDelta = sum(avgPriceGradient)/len(avgPriceGradient)
        retValue = []
        retValue.append(averageDelta)
        retValue.extend(avgPriceGradient)
        retValue.append(averagePriceDelta)
        # retValue.extend(diffBetweenDeltas)
        # retValue.extend(highestPriceGradient)
        # retValue.extend(lowPriceGradient)
        return retValue



    highestInflextionPointFeatures = getFeatureForInflection(
        [[data[maxPriceKey][0], data[maxPriceKey][1]] for data in highestInflexionPoints]
        )
    lowestInflextionPointsFeatures = getFeatureForInflection(
        [[data[lowPriceKey][0], data[lowPriceKey][1]] for data in lowestInflextionPoints]
        )

    retValue = (lowestInflextionPointsFeatures, highestInflextionPointFeatures)
    return retValue

def getDayOutlook(tickerData, earliestDay = None, latestDay = None, dayCountForFeatures = 120, dayCount = 3, symbolIndex = 0):
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

    for day in tickerData:
        currentDay = beginningOfTime + datetime.timedelta(days=(day))
        if day < earliestDayInt or day > latestDayInt:
            continue
        dayOfPrediction = int(day)
        openPrice = tickerData[day]["ticker"][0]
        highPrice = tickerData[day]["ticker"][2]
        lowPrice = tickerData[day]["ticker"][1]
        closePrice = tickerData[day]["ticker"][3]
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
        retryLimit = dayCount + 2
        while counter < retryLimit and len(nextDaySeriesIndexes)<=dayCount:
            dayIndex = day+counter
            if dayIndex in tickerData and dayIndex != day :
                activeDayCounter += 1
                dayData = tickerData[dayIndex]
                nextDaySeriesIndexes.append(dayData)
                sevenDayOpenPrice = dayData["ticker"][0]
                sevenDayHighPrice = dayData["ticker"][2]
                sevenDayClosePrice = dayData["ticker"][3]
                deltaOpen = sevenDayOpenPrice - closePrice
                deltaHigh = sevenDayHighPrice - closePrice
                deltaClose = sevenDayClosePrice - closePrice

                percentOpen = (deltaOpen/closePrice) * 100
                percentHigh = (deltaHigh/closePrice) * 100
                percentLow = (deltaClose/closePrice) * 100

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
                nextDaySeriesChanges.append([percentOpen, percentHigh, dayDiff, weekDay, percentLow])
            counter += 1

        
        retroTrainingDays = 0
        if not ignoreDay:
            possibleRetroDay = int(day) - dayCountForFeatures
            retryCount = 3
            foundEarliestDay = False
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
                        
                        while previousDayCounter > 0 and previousDayCountLoopLimit > 0:
                            previousDayCount -=1
                            if previousDayCount in tickerData:
                                previousDayCounter -= 1
                                finalPreviousDayIndex = previousDayCount
                                tradingDayCount += 1
                            previousDayCountLoopLimit -= 1

                        predictionDayHighDeltaPercent = ((highPrice - closePrice) / closePrice) * 100
                        predictionDayOpenDeltaPercent = ((openPrice - closePrice) / closePrice) * 100
                        predictionDayLowDeltaPercent = ((lowPrice - closePrice) / closePrice) * 100
                        dataForDay.append(predictionDayHighDeltaPercent)
                        # dataForDay.append(predictionDayOpenDeltaPercent)
                        dataForDay.append(predictionDayLowDeltaPercent)
                        
                        avgPriceCategory = int((retroDayAvgPrice)/10)
                        dataForDay.append(avgPriceCategory)


                        openPricePredictionDayDelta = retroDayOpeningPrice - closePrice
                        closePricePredictionDayDelta = retroDayClosingPrice - closePrice
                        highPricePredictionDayDelta = retroDayHighPrice - closePrice
                        lowPricePredictionDayDelta = retroDayLowPrice - closePrice
                        avgPricePredictionDayDelta = retroDayAvgPrice - closePrice

                        openPricePredictionDayDeltaPercent = (openPricePredictionDayDelta/closePrice) * 100
                        closePricePredictionDayDeltaPercent = (closePricePredictionDayDelta/closePrice) * 100
                        highPricePredictionDayDeltaPercent = (highPricePredictionDayDelta/closePrice) * 100
                        lowPricePredictionDayDeltaPercent = (lowPricePredictionDayDelta/closePrice) * 100
                        avgPricePredictionDayDeltaPercent = (avgPricePredictionDayDelta/closePrice) * 100
                        
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

                        inflectionPointFeatures = getPreceedingDayFeatures(dayOfPrediction, tickerData)
                        if inflectionPointFeatures is not None:
                            dataForDay.extend(inflectionPointFeatures[0])
                            dataForDay.extend(inflectionPointFeatures[1])
                            precedingNintyDays.extend(dataForDay)
                            retroTrainingDays +=1
                        featureLen = len(dataForDay)
                        if tickerFeaturesPerDay < featureLen:
                            tickerFeaturesPerDay = featureLen            
                    possibleRetroDay +=1
            
            desiredNumberOfRetroDaysForAnalysis = int(0.6667 * dayCountForFeatures) #We want to have at least two third of the count of the calendar days available as stock days
            if desiredNumberOfRetroDaysForAnalysis <= retroTrainingDays:
                if tickerFeaturesPerDay > 0:
                    dayLimit = desiredNumberOfRetroDaysForAnalysis * tickerFeaturesPerDay
                    deltaLimit = 1
                    if len(precedingNintyDays) > dayLimit:
                        precedingNintyDayCount = len(precedingNintyDays)
                        precedingNintyDays = precedingNintyDays[(precedingNintyDayCount - dayLimit):precedingNintyDayCount]
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
                            "symbolIndex": symbolIndex
                        }

    return retValue


def convertToTensors(tickerData, testRatio):
    resultToData = {}
    retValue = {}
    featureLengthPerRetroDay = None
    ignoreFeatureCount = None
    symbolKeys = list(tickerData.keys())
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
            precedingDays.append(symbolAndDayData)  # appending so can be removed in function reshapeData. To be used for assessing qualit of prediction
            ignoreFeatureCount = 1
            currentFeatureLengthPerRetroDay = dictOfDaysToPreceedingData[targetPredictionDayIndex]["featureLengthPerRetroDay"]
            if featureLengthPerRetroDay is None:
                featureLengthPerRetroDay = currentFeatureLengthPerRetroDay
            
            if featureLengthPerRetroDay != currentFeatureLengthPerRetroDay:
                raise NameError('It reeks, It reeks')

            if result in resultToData:
                resultToData[result].append(precedingDays)
            else:
                collection = []
                collection.append(precedingDays)
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


def reshapeData(xs, ys, featureLengthPerRetroDay, featureIgnoreCount = 0):
    tupleReformatedXs = [(paramFeatures[:len(paramFeatures) - featureIgnoreCount], paramFeatures[len(paramFeatures) - featureIgnoreCount:]) for paramFeatures in xs]
    reformatedXs = [onlyFeaturesAndSymbols[0] for onlyFeaturesAndSymbols in tupleReformatedXs]
    symbolAndFeatures = [onlyFeaturesAndSymbols[1] for onlyFeaturesAndSymbols in tupleReformatedXs]
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


def buildPredictionModel(trainData, trainResult, testData, testResult, featureLengthPerRetroDay, ignoreFeatureCount = 0, schewedData = None, symbolToIndex = None):
    
    combinedFeaturesPerDay = len(trainData[0]) - ignoreFeatureCount
    numberOfDays = combinedFeaturesPerDay/featureLengthPerRetroDay
    numberOfDaysAsInt = int(numberOfDays) # the number of retro days 

    testDataCount = len(testData)
    trainDataCount = len(trainData)

    print("We're training with "+str(trainDataCount) +" data points")
    print("We're testing with "+str(testDataCount) +" data points")

    reshaped = reshapeData(trainData, trainResult, featureLengthPerRetroDay, ignoreFeatureCount)
    trainDataReshaped = reshaped['x']
    trainResultReshaped = reshaped['y']
    metaData = reshaped['symbolAndFeatures']
    print(' metaData is '+ str(metaData[0]))
    optionCount = 2

    validationData = None
    if schewedData is not None:
        extraFeaturesData = schewedData[0]
        extraResults = schewedData[1]
        reshapedResults = reshapeData(extraFeaturesData, extraResults, featureLengthPerRetroDay, ignoreFeatureCount)
        validationData = (reshapedResults['x'], reshapedResults['y'])

    ###### Model creation 
    model = tf.keras.Sequential()
    model.add(layers.LSTM(256, input_shape =(numberOfDaysAsInt,featureLengthPerRetroDay), return_sequences=False, implementation=2))
    model.add(layers.Dropout(0.35))
    model.add(layers.Dense(256, activation='relu'),)
    model.add(layers.Dense(optionCount, activation='softmax'))

    numberOfEpochs = 200
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
        epochs=numberOfEpochs)

    reshaped = reshapeData(testData, testResult, featureLengthPerRetroDay, ignoreFeatureCount)
    testDataReshaped = reshaped['x']
    testResultReshaped = reshaped['y']
    test_loss, test_acc = model.evaluate(testDataReshaped,  testResultReshaped, verbose=2)
    print('\nTest accuracy:', test_acc)

    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()
    oneErrorRate(predictionArr, testResultReshaped, testData, prediction_probabilities, symbolToIndex)
    return model

def pickStockFromProbabilities(predictionProbability, numberOfStockForProbability = 5, stockPerDay = 1, probabilityRetryCount = 1000):
    orderedByBestProbability = sorted(predictionProbability, key=lambda Probabs: (Probabs["wrongProbability"]))
    bestFiveStocks = orderedByBestProbability[:numberOfStockForProbability]
    retValue = []
    if len(bestFiveStocks) > 0:
        poulatedByRandomness = []
        listGenCounter = 0
        while listGenCounter < len(bestFiveStocks):
            poulatedByRandomness.append({
                "counter": 0,
                "index": listGenCounter
            })
            listGenCounter+=1

        indexLimit = len(bestFiveStocks) - 1
        allIndexesToCount = []
        retryCounter = 0
        while retryCounter < probabilityRetryCount:
            ranDomIndex = random.randint(0, indexLimit)
            poulatedByRandomness[ranDomIndex]["counter"] += 1
            retryCounter +=1

        sortedRandomIndex = sorted(poulatedByRandomness, key=lambda entry: entry["counter"], reverse=True)
        selectedRandomIndexes = sortedRandomIndex[:stockPerDay]
        retValue = [bestFiveStocks[stockIndex['index']] for stockIndex in selectedRandomIndexes]

    else:
        retValue.append(bestFiveStocks[0])
    
    return retValue




    



def assessPredictions(model, testData, testResults, featureLengthPerRetroDay, ignoreFeatureCount, indexToSymbol, stockPerDay = 1):
    reshaped = reshapeData(testData, testResults, featureLengthPerRetroDay, ignoreFeatureCount)
    testDataReshaped = reshaped['x']
    testResultReshaped = reshaped['y']

    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()

    predictionProcessed = processPredictions(predictionArr, prediction_probabilities, testData, testResults, indexToSymbol)
    

    totalCorrectlyPredicted = 0
    totalOnesPredicted = 0


    if 1 in predictionProcessed:
        marketUpPredictions = predictionProcessed[1]
        for predictionDayIndex in marketUpPredictions:
            totalOnesPredicted += 1
            predictionDayStockPredictions = marketUpPredictions[predictionDayIndex]
            # for predictionDayIndex in predictionDayStockPredictions:
            # allStockPredictions = predictionDayStockPredictions[predictionDayIndex]
            selectedStocks = pickStockFromProbabilities(predictionDayStockPredictions)
            for selctedStock in selectedStocks:
                if selctedStock["result"] == 1:
                    totalCorrectlyPredicted += 1
    
    retValue = {
        'correctPredictions': totalCorrectlyPredicted,
        'totalOnesPredicted': totalOnesPredicted
    }

    return retValue


    


def oneErrorRate (prediction, result, testData, prediction_probabilities = None, indexToSymbol = None, printResult = False):
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
        tesDatum = testData[index]
        metadata = tesDatum[len(tesDatum) - 1]
        predictionValue = prediction[index]
        probs = None
        predictionAndIndex = None
        
        if prediction_probabilities is not None:
            probs = prediction_probabilities[index]
            predictionAndIndex = list(probs)
            # predictionAndIndex.append(metadata)
            symbolIndex = metadata["symbolIndex"]
            stockSymbol = indexToSymbol[symbolIndex]
            if indexToSymbol is not None:
                stockSymbol = indexToSymbol[symbolIndex]
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


def timeFromDayIndex(dayIndex):
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = beginningOfTime + datetime.timedelta(days=(dayIndex))

    return retValue

def processPredictions(predictions, predictionProbabilities, testData, testResults, indexToSymbol):
    OnePredicitons = {} # this holds a dayIndex -> ([topFiveProbabilityStockData], set(winningStocks))
    ZeroPredicitons = {}
    if (predictions is not None and predictionProbabilities is not None
        and testData is not None and testResults is not None
        and len(testResults) == len(predictionProbabilities) == len(predictions)):
        index = 0
        countLimit = len(predictions)
        while index < countLimit:
            tesDatum = testData[index]
            metadata = tesDatum[len(tesDatum) - 1]
            predictionDayIndex = metadata['targetPredictionDayIndex']
            predictionProbability = predictionProbabilities[index]
            symbolIndex = metadata["symbolIndex"]
            stockSymbol = indexToSymbol[symbolIndex]
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
        


def predict(model, indexToSymbol, testData, testResult, featureLengthPerRetroDay, ignoreFeatureCount):
    reshaped = reshapeData(testData, testResult, featureLengthPerRetroDay, ignoreFeatureCount)
    testDataReshaped = reshaped['x']
    testResultReshaped = reshaped['y']
    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()
    oneErrorRate(predictionArr, testResultReshaped, testData, prediction_probabilities, indexToSymbol)


def daysToDictionary(dayIndexes, mappings):
    retValue = {}
    for dayIndex in dayIndexes:
        retValue[dayIndex] = mappings[dayIndex]
    return retValue

# def retrieveTrainingDataFromJSON(dayIndexStart, dayIndexEnd, tickerSymbols, config = None):
#     loopStartTime = dayIndexStart
#     if config is None:
#         config = WeatherManPredictionTestConfig()
#     loopEndTime = loopStartTime + config.numberOfDaysForTraining

#     while loopEndTime < dayIndexEnd:
#         dataIndexToCounter = {}
#         symbolToDayData = {}
#         symbolCounter = 0
#         totalDays = years * daysPerYear
#         for symbol in tickerSymbols:
#             if symbol not in symbolToDayData:
#                 tickerData = load_time_series_daily(symbol)
#                 print("symbol is "+ str(symbol))
#                 stockDataDayCount = len(tickerData)
#                 if stockDataDayCount > totalDays:
#                     outlookResult = getDayOutlook(tickerData, loopStartTime, loopEndTime, symbolIndex = symbolCounter)
#                     symbolToDayData[symbol] = outlookResult
#                     dataIndexToCounter[symbolCounter] = symbol
#                     symbolCounter += 1
#                 else:
#                     print("Insufficient data for "+ symbol+"\nTotal days is : "+str(totalDays)+"\nStock Days is :"+str(stockDataDayCount))



def runExec(tickerSymbols = None):
    defaultSymbol = "MMM"
    currentTime = datetime.datetime.now()
    years = 0.3
    daysPerYear = 365
    totalDays = years * daysPerYear
    earliestTime = currentTime + datetime.timedelta(days=(-totalDays))
    finalTime = None;# earliestTime + datetime.timedelta(days=(60))
    if not tickerSymbols:
        tickerSymbols = [defaultSymbol]
    dataIndexToSymbol = {}
    symbolToDayData = {}
    symbolCounter = 0
    for symbol in tickerSymbols:
        if symbol not in symbolToDayData:
            tickerData = load_time_series_daily(symbol)
            print("symbol is "+ str(symbol))
            stockDataDayCount = len(tickerData)
            if stockDataDayCount > totalDays:
                outlookResult = getDayOutlook(tickerData, earliestTime, finalTime, symbolIndex = symbolCounter)
                symbolToDayData[symbol] = outlookResult
                dataIndexToSymbol[symbolCounter] = symbol
                symbolCounter += 1
            else:
                print("Insufficient data for "+ symbol+"\nTotal days is : "+str(totalDays)+"\nStock Days is :"+str(stockDataDayCount))

    if len(symbolToDayData) > 0:
        trainResult = []
        trainData = []
        testResult = []
        testData = []
        validation = None
        ignoreFeatureCount = 0


        futureDayCount = 28
        symbolFeatureLengthPerRetroDay = -3
        symbolKeys = symbolToDayData.keys()

        print("using the time frame "+str(earliestTime)+ " - "+str(finalTime))
        print("Predicting "+str(futureDayCount)+ " days into the future")

        for key in symbolKeys:
            trainingDays = None
            for value in symbolToDayData[key].values():
                trainingDays = value["trainingDays"]
                break
        
            if trainingDays is not None:
                orderedTraingDays = sorted(trainingDays)
                trainDataDays = orderedTraingDays[:len(orderedTraingDays) - futureDayCount]
                testDataDays = orderedTraingDays[(len(orderedTraingDays) - futureDayCount):]
                testSymbolToDayData = {
                    ""+key+"": daysToDictionary(testDataDays, symbolToDayData[key])
                }

                trainSymbolToDayData = {
                    ""+key+"": daysToDictionary(trainDataDays, symbolToDayData[key])
                }
                dataFormated = convertToTensors(trainSymbolToDayData, 0)
                trainResult.extend( dataFormated['trainY'])
                trainData.extend(dataFormated['trainX'])
                testResult.extend(dataFormated['testY'])
                testData.extend(dataFormated['testX'])

                dataFormated = convertToTensors(testSymbolToDayData, 1)
                trainResult.extend( dataFormated['trainY'])
                trainData.extend(dataFormated['trainX'])
                testResult.extend(dataFormated['testY'])
                testData.extend(dataFormated['testX'])
                etFeatureDayLength = dataFormated['featureLengthPerRetroDay']
                ignoreFeatureCount = dataFormated['ignoreFeatureCount']
                symbolFeatureLengthPerRetroDay = etFeatureDayLength
                

        
        model = buildPredictionModel(trainData,trainResult,testData, testResult, symbolFeatureLengthPerRetroDay, ignoreFeatureCount, (testData, testResult), dataIndexToSymbol)
        modelAssessment = assessPredictions(model, testData, testResult, symbolFeatureLengthPerRetroDay, ignoreFeatureCount, dataIndexToSymbol)
        print(str(modelAssessment))
        
        finalAccuracy = (modelAssessment['correctPredictions']/ modelAssessment['totalOnesPredicted']) * 100
        print("Bidding accuracy is "+str(finalAccuracy))
    else:
        print("Could not find data to process")

