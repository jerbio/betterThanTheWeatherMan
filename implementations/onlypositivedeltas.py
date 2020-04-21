import json
import datetime
import random
import tensorflow as tf
from tensorflow import keras

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from libfiles.loadDataSeries import load_time_series_daily



# This works by looking forward into a given number of days from a given day.
# It generates a collecion of all the deltass of the future days high from the a given days opening price
# Any day with delta higher than 'deltaLimit' will be set to some max value



tickerData = load_time_series_daily("AMD")




def getDayOutlook(tickerData, earliestDay, dayCount = 3):
    '''
    function generates a 'dayCount' day data of the stock market it gets the percentage hikes of each day after a given day
    '''
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {

    }
    for day in tickerData:
        dayAsInt = int(day)
        currentDay = beginningOfTime + datetime.timedelta(days=(day))
        openPrice = tickerData[day]["ticker"][0]
        highPrice = tickerData[day]["ticker"][2]
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
        while counter < dayCount and len(nextDaySeriesIndexes)<3:
            dayIndex = day+counter
            if dayIndex in tickerData:
                activeDayCounter += 1
                dayData = tickerData[dayIndex]
                nextDaySeriesIndexes.append(dayData)
                sevenDayOpenPrice = dayData["ticker"][0]
                sevenDayHighPrice = dayData["ticker"][2]
                deltaOpen = sevenDayOpenPrice - openPrice
                deltaHigh = sevenDayHighPrice - openPrice

                percentOpen = (deltaOpen/openPrice) * 100
                percentHigh = (deltaHigh/openPrice) * 100
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


                if percentOpen > 0 and percentOpen > maxPositive:
                    maxPositive = percentOpen
                if percentHigh > 0 and percentHigh > maxPositive:
                    maxPositive = percentHigh

                if percentOpen < 0 and percentOpen < maxNegative:
                    maxNegative = percentOpen
                if percentHigh < 0 and percentHigh < maxNegative:
                    maxNegative = percentHigh
                

                nextDaySeriesChanges.append([percentOpen, percentHigh, dayDiff, weekDay])
            counter += 1
        
        if not ignoreDay:
            earliestPossibleDay = int(day) - 90
            retryCount = 3
            foundEarliestDay = False
            while retryCount > 0:
                if earliestPossibleDay in tickerData:
                    foundEarliestDay = True
                    break
                earliestPossibleDay -= 1
                retryCount -= 1
            
            if foundEarliestDay:
                while earliestPossibleDay < dayAsInt:
                    if earliestPossibleDay in tickerData:
                        featureDay = beginningOfTime + datetime.timedelta(days=(earliestPossibleDay))
                        weekDay = featureDay.weekday()
                        tickerEntry = tickerData[earliestPossibleDay]
                        precedingNintyDays.append(tickerEntry['ticker'][0])
                        precedingNintyDays.append(tickerEntry['ticker'][1])
                        precedingNintyDays.append(tickerEntry['ticker'][2])
                        precedingNintyDays.append(tickerEntry['ticker'][3])
                        precedingNintyDays.append(weekDay)
                    earliestPossibleDay +=1
            dayLimit = 90
            deltaLimit = 2
            if len(precedingNintyDays) > 30:
                dayCount = len(precedingNintyDays)
                precedingNintyDays = precedingNintyDays[(dayCount - dayLimit):dayCount]
                maxDelta = 1 if maxPositive > deltaLimit else 0
                retValue[day] = {
                    "maxDelta": maxDelta,
                    "changes": nextDaySeriesChanges,
                    "tickerData": nextDaySeriesIndexes,
                    "precedingDays": precedingNintyDays
                }
    return retValue


def convertToTensors(dictOfPrecedingDaysTo, testRatio):
    resultToData = {}
    retValue = {}

    for dayCount in dictOfPrecedingDaysTo:
        precedingDays = dictOfPrecedingDaysTo[dayCount]["precedingDays"]
        result = dictOfPrecedingDaysTo[dayCount]["maxDelta"]
        if result in resultToData:
            resultToData[result].append(precedingDays)
        else:
            collection = []
            collection.append(precedingDays)
            resultToData[result] = collection

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
        

        for dataSeries in allData:
            isForTest = False
            # dataSeries = allData[index]
            if testCount > 0:
                isForTest = bool(random.getrandbits(1))
                testCount -=1
            if isForTest:
                testData.append(dataSeries)
                testResult.append(percentToIndex[result])
            else:
                trainData.append(dataSeries)
                trainResult.append(percentToIndex[result])
        
        # retValue[result] = (testData, trainData)


    optionCount = len(resultToData)

    model = keras.Sequential([
        # keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(16, activation='relu'),
        keras.layers.Dense(optionCount)
    ])
    numberOfEpochs = 100
    learningRate = 0.001
    optimizer = tf.compat.v1.train.AdamOptimizer(
        learning_rate=learningRate, beta1=0.9, beta2=0.999, epsilon=1e-08, use_locking=False,
        name='Adam'
    )
    model.compile(optimizer=optimizer,
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])

    trainData_tf= tf.convert_to_tensor(trainData)
    trainResult_tf= tf.convert_to_tensor(trainResult)
    model.fit(trainData, trainResult, epochs=numberOfEpochs)

    test_loss, test_acc = model.evaluate(testData,  testResult, verbose=2)
    print('\nTest accuracy:', test_acc)
        


def runExec():
    constDayNumber = 678687647816781687
    earliestDay = constDayNumber

    for key in tickerData.keys():
        dayIndex = int(key)
        if dayIndex < earliestDay:
            earliestDay = dayIndex

    if earliestDay != constDayNumber:
        outlookResult = getDayOutlook(tickerData, earliestDay)
        # print(outlookResult);
        
        convertToTensors(outlookResult, 0.3)
        
        jsonDump = json.dumps(outlookResult)