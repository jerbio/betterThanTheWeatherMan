import datetime
import json
import os
from pathlib import Path

def dayIndexFromTime(time):
    '''
        Giving a time after 1970 Jan 1 this function returns the number of days from 1970 Jan 1 12:00 AM rounded down
    '''
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')

    retValue = int((time - beginningOfTime).days)
    return retValue


def timeFromDayIndex(dayIndex):
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = beginningOfTime + datetime.timedelta(days=(dayIndex))

    return retValue

def msToTime(msTime):
    retValue = datetime.datetime.now() + datetime.timedelta(milliseconds=msTime)
    return retValue


def timeToMs(dateTimeObj):
    epoch = datetime.datetime.utcfromtimestamp(0)
    retValue = (dateTimeObj - epoch).total_seconds() * 1000.0
    return retValue


def getSymbolTickerDataForDayIndex(allSymbolsToTickerData, symbol, dayIndex):
    retValue = allSymbolsToTickerData[symbol]['symbolData'][dayIndex]['ticker']
    return retValue

def getDayIndexes(allSymbolsToTickerData, symbol, dayIndex, count):
    formatedIndexesData = allSymbolsToTickerData[symbol]["formatedIndexes"]
    dayIndexDict = formatedIndexesData['dayIndexToListIndex']
    dayIndexList = formatedIndexesData['orderedDayIndex']
    indexInOrderedList = dayIndexDict[dayIndex]
    endOfIndex = indexInOrderedList + count
    retValue = dayIndexList[indexInOrderedList: endOfIndex]
    return retValue


def load_prediction(predicitonFilePath = None):
    defaultFolderPath = ".\\notpinky\\predictionDump\\lightningStrikes\\"
    filePath = predicitonFilePath
    retValue = None
    if predicitonFilePath is None:
        walk = os.walk
        predicitonFilePath = str(Path(defaultFolderPath))
        filePath = predicitonFilePath
        predictionFolderNames = []
        for (dirpath, dirnames, filenames) in walk(predicitonFilePath):
            predictionFolderNames.extend(list(dirnames))

        sortedPredictionFolderNames = sorted(predictionFolderNames, reverse = True)
        if len(sortedPredictionFolderNames) > 0:
            filePath += "\\" + sortedPredictionFolderNames[0]
            filePath += '\\prediction.json'

    with open(filePath) as f:
        retValue = json.load(f)


    return retValue 


def getDayIndexes(orderedDayIndexes, dayIndexToIndexInList, referenceDayIndex, dayIndexDelta):
    ''' 
        function gets the next or preceding dayIndexes from referenceDayIndex.
        If dayIndexDelta is positive it is next dayIndexDelta inclusive of referenceDayIndex
        else if its negative it is preceding dayIndexDelta inclusive of referenceDayIndex
        The length of the returned array should be equal or less than the absolute value of dayIndexDelta
    '''
    indexInList = dayIndexToIndexInList[referenceDayIndex]
    orderedDayIndexes[indexInList]
    retValue = []
    beginIndex = None
    finalIndex = None
    if dayIndexDelta != 0:
        if dayIndexDelta > 0:
            finalIndex = indexInList+dayIndexDelta
            beginIndex = indexInList
        else:
            finalIndex = indexInList+1
            beginIndex += dayIndexDelta
            if beginIndex < 0:
                beginIndex = 0

    retValue = orderedDayIndexes[beginIndex: finalIndex]

    return retValue