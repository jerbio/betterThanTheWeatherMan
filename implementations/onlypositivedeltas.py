import json
import datetime
import random
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
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
tickerFeaturesPerDay = -1
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

def getDayOutlook(tickerData, earliestDay = None, latestDay = None, dayCount = 3):
    '''
    function generates a 'dayCount' day data of the stock market it gets the percentage hikes of each day after a given day, excluding the current day
    earliestDay holds the earliest day to which you don't want to pull ticker data
    '''
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {

    }
    global tickerFeaturesPerDay
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
        closePrice = tickerData[day]["ticker"][3]
        nextDaySeriesIndexes = []
        nextDaySeriesChanges = []
        precedingNintyDays = []
        counter = 0
        activeDayCounter = 0
        isNegative = False
        highestDelta = 0
        ignoreDay = False
        maxPositive = 0
        maxNegative = 0
        while counter < (dayCount+1) and len(nextDaySeriesIndexes)<4:
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


                nextDaySeriesChanges.append([percentOpen, percentHigh, dayDiff, weekDay, percentLow])
            counter += 1

        dayCountForFeatures = 120
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
                        tickerEntry = tickerData[possibleRetroDay]
                        dataForDay = []
                        fiveDayAvgPriceDelta = None
                        previousDayCountLimit = 4
                        previousDayCounter = previousDayCountLimit
                        previousDayCount = possibleRetroDay
                        previousDayCountLoopLimit = previousDayCountLimit + 4
                        finalPreviousDayIndex = possibleRetroDay
                        tradingDayCount = 0
                        while previousDayCounter > 0 and previousDayCountLoopLimit > 0:
                            previousDayCount -=1
                            if previousDayCount in tickerData:
                                previousDayCounter -= 1
                                finalPreviousDayIndex = previousDayCount
                                tradingDayCount += 1
                            previousDayCountLoopLimit -= 1

                        avgPriceCategory = int((tickerEntry['ticker'][4])/10)
                        openCloseDelta = tickerEntry['ticker'][3] - tickerEntry['ticker'][0]
                        openLowDelta = tickerEntry['ticker'][1] - tickerEntry['ticker'][0]
                        openHighDelta = tickerEntry['ticker'][2] - tickerEntry['ticker'][0]
                        highLowDelta = tickerEntry['ticker'][2] - tickerEntry['ticker'][1]
                        if previousDayCounter != previousDayCountLimit:
                            previousDayTickerEntry = tickerData[finalPreviousDayIndex]
                            fiveDayAvgPriceDelta = (tickerEntry['ticker'][4] - previousDayTickerEntry['ticker'][4])


                        percentOpenCloseDelta = (openCloseDelta / tickerEntry['ticker'][0]) *100
                        percentHighDelta = (openHighDelta / tickerEntry['ticker'][0]) * 100
                        percentOpenLowDelta = (openLowDelta / tickerEntry['ticker'][0])*100
                        percentHighLowDelta = (highLowDelta / tickerEntry['ticker'][0])*100

                        percentCloseDelta = (openHighDelta / tickerEntry['ticker'][3])* 100
                        percentCloseLowDelta = (openLowDelta / tickerEntry['ticker'][3]) * 100
                        percentCloseHighDelta = (highLowDelta / tickerEntry['ticker'][3]) * 100
                        dataForDay.append(percentCloseDelta)
                        dataForDay.append(percentCloseLowDelta)
                        dataForDay.append(percentCloseHighDelta)

                        dataForDay.append(percentOpenCloseDelta)
                        dataForDay.append(percentHighDelta)
                        dataForDay.append(percentOpenLowDelta)
                        dataForDay.append(percentHighLowDelta)
                        dataForDay.append(avgPriceCategory)

                        tradingDayDelta = 0
                        percentageTradingDayDelta = 0
                        if fiveDayAvgPriceDelta is None:
                            percentFiveDayDelta = percentOpenCloseDelta
                        else:
                            percentFiveDayDelta = (fiveDayAvgPriceDelta/tickerEntry['ticker'][0])
                            tradingDayDelta = fiveDayAvgPriceDelta/tradingDayCount
                            percentageTradingDayDelta = ((fiveDayAvgPriceDelta/tickerEntry['ticker'][0]) * 100)/tradingDayCount
                        
                        dataForDay.append(percentFiveDayDelta)
                        dataForDay.append(tradingDayDelta)
                        dataForDay.append(percentageTradingDayDelta)

                        dataForDay.append(tickerEntry['ticker'][0])
                        dataForDay.append(tickerEntry['ticker'][1])
                        dataForDay.append(tickerEntry['ticker'][2])
                        dataForDay.append(tickerEntry['ticker'][3])
                        dataForDay.append(tickerEntry['ticker'][4])
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
                        dayCount = len(precedingNintyDays)
                        precedingNintyDays = precedingNintyDays[(dayCount - dayLimit):dayCount]
                        maxDelta = 1 if maxPositive > deltaLimit else 0
                        retValue[day] = {
                            "day": day,
                            "maxDelta": maxDelta,
                            "changes": nextDaySeriesChanges,
                            "tickerData": nextDaySeriesIndexes,
                            "precedingDays": precedingNintyDays,
                            "featureLengthPerRetroDay": featureLen
                        }

    return retValue


def convertToTensors(tickerData, testRatio):
    resultToData = {}
    retValue = {}
    featureLengthPerRetroDay = None
    symbolKeys = list(tickerData.keys())
    random.shuffle(symbolKeys)
    for symbolKey in symbolKeys:
        dictOfPrecedingDaysTo = tickerData[symbolKey]
        for dayCount in dictOfPrecedingDaysTo:
            precedingDays = dictOfPrecedingDaysTo[dayCount]["precedingDays"]
            result = dictOfPrecedingDaysTo[dayCount]["maxDelta"]
            currentFeatureLengthPerRetroDay = dictOfPrecedingDaysTo[dayCount]["featureLengthPerRetroDay"]
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
    ##### End of section removing schewed data
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
                testResult.append(percentToIndex[result])
            else:
                trainData.append(dataSeries)
                trainResult.append(percentToIndex[result])


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
        'schewData': None
    }

    if restOfSchewedCollection is not None and len(restOfSchewedCollection) > 0:
        retValue['schewData'] =  {'data': restOfSchewedCollection, 'key':scheduedKeys}
    return retValue


def reshapeData(xs, ys, featureLengthPerRetroDay):
    combinedFeaturesPerDay = len(xs[0])
    numberOfDays = combinedFeaturesPerDay/featureLengthPerRetroDay
    numberOfDaysAsInt = int(numberOfDays) # the number of retro days 

    dataCount = len(xs)
    reshapedX = array(xs)
    reshapedX = reshapedX.reshape(dataCount, numberOfDaysAsInt, featureLengthPerRetroDay)
    reshapedX = reshapedX.tolist()
    return {
        'x': reshapedX,
        'y': ys
    }


def buildModelAndPredictModel(trainData, trainResult, testData, testResult, featureLengthPerRetroDay, schewedData = None, model = None):
    
    combinedFeaturesPerDay = len(trainData[0])
    numberOfDays = combinedFeaturesPerDay/featureLengthPerRetroDay
    numberOfDaysAsInt = int(numberOfDays) # the number of retro days 

    testDataCount = len(testData)
    trainDataCount = len(trainData)

    print("We're training with "+str(trainDataCount) +" data points")
    print("We're testing with "+str(testDataCount) +" data points")

    reshaped = reshapeData(trainData, trainResult, featureLengthPerRetroDay)
    trainDataReshaped = reshaped['x']
    trainResultReshaped = reshaped['y']
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
    model.add(layers.Dropout(0.40))
    model.add(layers.Dense(256, activation='relu'),)
    model.add(layers.Dense(optionCount, activation='softmax'))

    numberOfEpochs = 1000
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

    reshaped = reshapeData(testData, testResult, featureLengthPerRetroDay)
    testDataReshaped = reshaped['x']
    testResultReshaped = reshaped['y']
    test_loss, test_acc = model.evaluate(testDataReshaped,  testResultReshaped, verbose=2)
    print('\nTest accuracy:', test_acc)

    prediction = model.predict(testDataReshaped, verbose=2)
    prediction_probabilities = list(prediction)

    prediction = model.predict_classes(testDataReshaped, verbose=2)
    predictionArr = prediction.tolist()
    oneErrorRate(predictionArr, testResultReshaped, prediction_probabilities)


def oneErrorRate (prediction, result, prediction_probabilities = None):
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
        predictionValue = prediction[index]
        probs = None
        predictionAndIndex = None
        
        if prediction_probabilities is not None:
            probs = prediction_probabilities[index]
            predictionAndIndex = list(probs)
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
    
    sortedOnlyOneCounts = sorted(onlyOneCounts, key=lambda Probabs: Probabs[0])
    
    # print("correct prediction count " + str(correctOneCountPrediction))
    # print("one prediction count " + str(onePredictionCount))
    # print("CombinedPredictions count " + str(onlyOneCounts))
    print("Sorted CombinedPredictions count " + str(sortedOnlyOneCounts))
    # print("\n\n\n\nWrong prediction probablities \n" + str(FailedPredictions))
    # print("\n\n\n\nCorrect prediction probablities \n" + str(SuccessfullPredictions))


def runExec(tickerSymbols = None):
    defaultSymbol = "MMM"
    constDayNumber = 678687647816781687
    earliestDayInTickerData = constDayNumber
    currentTime = datetime.datetime.now()
    years = 1
    daysPerYear = 365
    totalDays = years * daysPerYear
    earliestTime = currentTime + datetime.timedelta(days=(-totalDays))
    if not tickerSymbols:
        tickerSymbols = [defaultSymbol]

    symbolToDayData = {}
    for symbol in tickerSymbols:
        if symbol not in symbolToDayData:
            tickerData = load_time_series_daily(symbol)
            print("symbol is "+ str(symbol))
            stockDataDayCount = len(tickerData)
            if stockDataDayCount > totalDays:
                outlookResult = getDayOutlook(tickerData, earliestTime)
                symbolToDayData[symbol] = outlookResult
            else:
                print("Insufficient data for "+ symbol+"\nTotal days is : "+str(totalDays)+"\nStock Days is :"+str(stockDataDayCount))

    if len(symbolToDayData) > 0:
        dataFormated = convertToTensors(symbolToDayData, 0.3)
        trainResult = dataFormated['trainY']
        trainData = dataFormated['trainX']
        testResult = dataFormated['testY']
        testData  = dataFormated['testX']
        validation = None
        if dataFormated['schewData']:
            validationData  = dataFormated['schewData']['data']
            validationResult  = dataFormated['schewData']['key']
            validation = (validationData, validationResult)
        featureLengthPerRetroDay = dataFormated['featureLengthPerRetroDay']
        buildModelAndPredictModel(trainData,trainResult,testData, testResult, featureLengthPerRetroDay, validation )

    else:
        print("Could not find data to process")

