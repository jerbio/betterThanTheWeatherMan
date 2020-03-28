import json
import datetime
from  loadDataSeries import load_time_series_daily

tickerData = load_time_series_daily("GOOG")


def getSevenDayOutlook(tickerData):
    '''
    function generates a seven day data of the stock market it gets the percentage hikes of each day after a given day
    '''
    beginningOfTime_str = "1970-01-01 00:00:00";
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {

    }
    for day in tickerData:
        currentDay = beginningOfTime + datetime.timedelta(days=(day));
        openPrice = tickerData[day]["ticker"][0]
        highPrice = tickerData[day]["ticker"][2]
        nextSevenDaysIndexes = [];
        nextSevenDaysChanges = [];
        counter = 0
        activeDayCounter = 0
        while counter < 7 and len(nextSevenDaysIndexes)<5:
            dayIndex = day+counter;
            if dayIndex in tickerData:
                activeDayCounter += 1;
                dayData = tickerData[dayIndex];
                nextSevenDaysIndexes.append(dayData);
                sevenDayOpenPrice = dayData["ticker"][0];
                sevenDayHighPrice = dayData["ticker"][2];
                deltaOpen = sevenDayOpenPrice - openPrice;
                deltaHigh = sevenDayHighPrice - openPrice;

                percentOpen = (deltaOpen/openPrice) * 100;
                percentHigh = (deltaHigh/openPrice) * 100;
                dayDiff = counter;
                outlookDay = currentDay + datetime.timedelta(days=(dayDiff))
                weekDay = outlookDay.weekday()
                nextSevenDaysChanges.append([percentOpen, percentHigh, dayDiff, weekDay])
            counter += 1;
        retValue[day] = {
            "changes": nextSevenDaysChanges,
            "tickerData": nextSevenDaysIndexes
        };
    return retValue;

outlookResult = getSevenDayOutlook(tickerData);
# print(outlookResult);
jsonDump = json.dumps(outlookResult)
print(jsonDump);