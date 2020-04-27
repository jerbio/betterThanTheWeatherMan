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

        retValue = []
        retValue.append(averageDelta)
        retValue.extend(avgPriceGradient)
        retValue.extend(diffBetweenDeltas)
        retValue.extend(highestPriceGradient)
        retValue.extend(lowPriceGradient)
        return retValue



    highestInflextionPointFeatures = getFeatureForInflection(
        [[data[maxPriceKey][0], data[maxPriceKey][1]] for data in highestInflexionPoints]
        )
    lowestInflextionPointsFeatures = getFeatureForInflection(
        [[data[lowPriceKey][0], data[lowPriceKey][1]] for data in lowestInflextionPoints]
        )

    retValue = (lowestInflextionPointsFeatures, highestInflextionPointFeatures)
    return retValue

def getDayOutlook(tickerData, earliestDay = None, dayCount = 3):
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
    if earliestDay:
        earliestDayInt = (earliestDay - beginningOfTime).days

    for day in tickerData:
        currentDay = beginningOfTime + datetime.timedelta(days=(day))
        if day < earliestDayInt:
            continue
        dayAsInt = int(day)
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
                deltaOpen = sevenDayOpenPrice - closePrice
                deltaHigh = sevenDayHighPrice - closePrice

                percentOpen = (deltaOpen/closePrice) * 100
                percentHigh = (deltaHigh/closePrice) * 100
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

                # if highestDelta > 3:#ignore days with higher than 4% swings
                #     ignoreDay = True
                #     break

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

        dayCountForFeatures = 90
        if not ignoreDay:
            earliestPossibleDay = int(day) - dayCountForFeatures
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
                        dataForDay = []
                        fiveDayAvgPriceDelta = None
                        previousDayCountLimit = 4
                        previousDayCounter = previousDayCountLimit
                        previousDayCount = earliestPossibleDay
                        previousDayCountLoopLimit = previousDayCountLimit + 4
                        finalPreviousDayIndex = earliestPossibleDay
                        tradingDayCount = 0
                        while previousDayCounter > 0 and previousDayCountLoopLimit > 0:
                            previousDayCount -=1
                            if previousDayCount in tickerData:
                                previousDayCounter -= 1
                                finalPreviousDayIndex = previousDayCount
                                tradingDayCount += 1
                            previousDayCountLoopLimit -= 1

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
                        percentCloseLowDelta = (highLowDelta / tickerEntry['ticker'][3]) * 100
                        dataForDay.append(percentCloseDelta)
                        dataForDay.append(percentCloseLowDelta)
                        dataForDay.append(percentCloseLowDelta)

                        dataForDay.append(percentOpenCloseDelta)
                        dataForDay.append(percentHighDelta)
                        dataForDay.append(percentOpenLowDelta)
                        dataForDay.append(percentHighLowDelta)

                        tradingDayDelta = 0
                        percentageTradingDayDelta = 0
                        if fiveDayAvgPriceDelta is None:
                            percentFiveDayDelta = percentOpenCloseDelta;
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

                        inflectionPointFeatures = getPreceedingDayFeatures(dayAsInt, tickerData)
                        if inflectionPointFeatures is not None:
                            dataForDay.extend(inflectionPointFeatures[0])
                            dataForDay.extend(inflectionPointFeatures[1])
                            precedingNintyDays.extend(dataForDay)
                        # dataForDay.append(weekDay)
                        featureLen = len(dataForDay)
                        if tickerFeaturesPerDay < featureLen:
                            tickerFeaturesPerDay = featureLen
                        
                        
                    earliestPossibleDay +=1
            dayLimit = dayCountForFeatures - 30

            if tickerFeaturesPerDay > 0:
                dayLimit = dayLimit * tickerFeaturesPerDay
            deltaLimit = 1
            if len(precedingNintyDays) > dayLimit:
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


def convertToTensors(tickerData, testRatio):
    resultToData = {}
    retValue = {}

    for key in tickerData:
        dictOfPrecedingDaysTo = tickerData[key]
        for dayCount in dictOfPrecedingDaysTo:
            precedingDays = dictOfPrecedingDaysTo[dayCount]["precedingDays"]
            result = dictOfPrecedingDaysTo[dayCount]["maxDelta"]
            if result in resultToData:
                resultToData[result].append(precedingDays)
            else:
                collection = []
                collection.append(precedingDays)
                resultToData[result] = collection


    minCount = None
    for key in resultToData:
        count = len(resultToData[key])
        if minCount is None or count < minCount:
            minCount = count

    for key in resultToData:
        resultToData[key] = resultToData[key][:minCount]

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
    randomPause=9
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

        # retValue[result] = (testData, trainData)


    optionCount = len(resultToData)

    model = keras.Sequential([
        # keras.layers.Flatten(input_shape=(28, 28)),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dense(optionCount)
    ])
    numberOfEpochs = 100
    learningRate = 0.001
    optimizer = tf.compat.v1.train.AdamOptimizer(
        learning_rate=learningRate, beta1=0.9, beta2=0.999, epsilon=1e-08, use_locking=False,
        name='Adam'
    )
    # optimizer = tf.compat.v1.train.GradientDescentOptimizer(
    #     learning_rate = learningRate, use_locking=False, name='GradientDescent'
    # )
    model.compile(optimizer=optimizer,
                loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                metrics=['accuracy'])

    trainData_tf= tf.convert_to_tensor(trainData)
    trainResult_tf= tf.convert_to_tensor(trainResult)
    model.fit(trainData, trainResult, epochs=numberOfEpochs)

    test_loss, test_acc = model.evaluate(testData,  testResult, verbose=2)
    print('\nTest accuracy:', test_acc)



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
        convertToTensors(symbolToDayData, 0.3)
    else:
        print("Could not find data to process")

