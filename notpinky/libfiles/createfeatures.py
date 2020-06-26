import json
import datetime
from  loaddataseries import load_time_series_daily

tickerData = load_time_series_daily("AMD")




def getSevenDayOutlook(tickerData, earliestDay):
    '''
    function generates a seven day data of the stock market it gets the percentage hikes of each day after a given day
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
        nextSevenDaysIndexes = []
        nextSevenDaysChanges = []
        precedingNintyDays = []
        counter = 0
        activeDayCounter = 0
        isNegative = False
        highestDelta = 0
        while counter < 7 and len(nextSevenDaysIndexes)<5:
            dayIndex = day+counter
            if dayIndex in tickerData:
                activeDayCounter += 1
                dayData = tickerData[dayIndex]
                nextSevenDaysIndexes.append(dayData)
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

                nextSevenDaysChanges.append([percentOpen, percentHigh, dayDiff, weekDay])
            counter += 1
        
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

        if len(precedingNintyDays) > 30:
            peakDelta = 5 if  highestDelta > 5 else highestDelta
            retValue[day] = {
                "maxDelta": (-1 * peakDelta) if isNegative  else peakDelta,
                "changes": nextSevenDaysChanges,
                "tickerData": nextSevenDaysIndexes
                
                # "precedingDays": precedingNintyDays
            }
    return retValue

constDayNumber = 678687647816781687
earliestDay = constDayNumber

for key in tickerData.keys():
    dayIndex = int(key)
    if dayIndex < earliestDay:
        earliestDay = dayIndex

if earliestDay != constDayNumber:
    outlookResult = getSevenDayOutlook(tickerData, earliestDay)
    # print(outlookResult);
    jsonDump = json.dumps(outlookResult)
    print(jsonDump)