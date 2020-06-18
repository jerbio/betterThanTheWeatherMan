import datetime

def dayIndexFromStart(time):
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
