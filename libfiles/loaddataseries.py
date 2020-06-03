import os
import json
import datetime
# from ..weatherutility import msToTime, timeToMs
from .downloadstockdata import downloadStockBySymbol
from .tickerSelector import polygonIo, alphaVantage, tingo
import pytz
from tzlocal import get_localzone 

# closeKeyString = "4. close"
# openKeyString = "1. open"
# highKeyString = "2. high"
# lowKeyString = "3. low"
# volumeKeyString = "5. volume"

currentStockTicker = tingo

def getStockFileNames(symbol, series_type, folderPath = None):
    walk = os.walk;
    # series_type = "TIME_SERIES_DAILY";
    dirname = os.path.dirname(__file__)
    retValue = {};
    folderPath =  "..\\TrainingData\\StockDump\\" if folderPath is None else folderPath
    fullFolderPath = folderPath+series_type+"\\"+symbol+"\\";
    pathFoFolder = dirname+"\\" + fullFolderPath
    fullFolderPath = pathFoFolder
    for (dirpath, dirnames, filenames) in walk(fullFolderPath):
        for fileName in filenames:
            fullFileName = fullFolderPath+fileName;
            retValue[fileName] = (fileName, fullFileName);
    
    return retValue


def extrapolateClosingPrice(tickerDataPoints, extraPolateSpanInMs):
    earliestTicker = None
    latestTicker = None
    epoch = datetime.datetime.utcfromtimestamp(0)
    orderedTickerDataPoints = sorted(tickerDataPoints, key=lambda entry: entry['date'])[len(tickerDataPoints) - 2 :len(tickerDataPoints)]
    
    if len(orderedTickerDataPoints) > 0:
        for tickerInstance in orderedTickerDataPoints:
            tickerDateString = tickerInstance['date']
            dateObject = datetime.datetime.strptime(tickerDateString, '%Y-%m-%dT%H:%M:%S.%fZ')
            dateInMs = (dateObject - epoch).total_seconds() * 1000.0

            if earliestTicker is None or earliestTicker['dateInMs'] > dateInMs:
                earliestTicker = {
                    'dateInMs': dateInMs,
                    'tickerData': tickerInstance,
                    'avg': ((tickerInstance['close'] + tickerInstance['open'])/2)
                }
            
            if latestTicker is None or latestTicker['dateInMs'] < dateInMs:
                latestTicker = {
                    'dateInMs': dateInMs,
                    'tickerData': tickerInstance,
                    'avg': ((tickerInstance['close'] + tickerInstance['open'])/2)
                }

    if earliestTicker is not None and latestTicker is not None:
        gradientBias = 0.95 # this is because of trying to add some inherent bias. Looks like towards the last 5 minutes gradients soften bbecause of less volume in general
        priceDelta = (latestTicker['avg'] - earliestTicker['avg']) * gradientBias
        timeDelta = (latestTicker['dateInMs'] - earliestTicker['dateInMs'])
        priceGradient = (priceDelta/timeDelta)
        extraPolatedPriceDelta = extraPolateSpanInMs * priceGradient
        retValue = {
            'priceDelta': extraPolatedPriceDelta,
        }

        return retValue
    else:
        return None

def getTimeSeriesFromIntraDaily(intraDayObject, nowTimeObj, preecedingMinuteSpan = 15):
    closeKeyString = tingo.close
    openKeyString = tingo.open
    highKeyString = tingo.high
    lowKeyString = tingo.low
    volumeKeyString = tingo.volume

    thirtyMinTimeSpan = preecedingMinuteSpan * 60

    
    lastThirtyMin = nowTimeObj - datetime.timedelta(seconds=thirtyMinTimeSpan)

    lastThirtyMinSpanTicker = []

    openPrice = None
    closePrice = None
    lowPrice = None
    highPrice = None
    volume = 0

    
    if len(intraDayObject) > 0:
        firstTicker = intraDayObject[0]
        lastTicker = intraDayObject[len(intraDayObject) - 1]
        openPrice = float(firstTicker[openKeyString])
        closePrice = float(lastTicker[closeKeyString])
        reversedIntraDayObject = list(intraDayObject)
        reversedIntraDayObject.reverse() # reverse for ease of troubleshooting. THe latest times are the most relevant
        for tickerInstance in reversedIntraDayObject:
            lowestPriceIter = float(tickerInstance[lowKeyString])
            highstPriceIter = float(tickerInstance[highKeyString])
            dateTimeString = tickerInstance['date']
            # volumeIter = float(tickerInstance[volumeKeyString])
            # volume += volumeIter

            if lowPrice is None or lowestPriceIter < lowPrice:
                lowPrice = lowestPriceIter

            if highPrice is None or highstPriceIter > highPrice:
                highPrice = highstPriceIter
        
            timeObj = datetime.datetime.strptime(dateTimeString, "%Y-%m-%dT%H:%M:%S.%fZ")
            timeObj = timeObj.replace(tzinfo=datetime.timezone.utc)

            eastern = pytz.timezone('America/New_York')
            # eastern_timeObj = eastern.localize(timeObj)
            eastern_timeObj = timeObj.astimezone(eastern)

            if(timeObj < nowTimeObj and timeObj > lastThirtyMin):
                lastThirtyMinSpanTicker.append(tickerInstance)
        retValue = {
            "timeObj": timeObj,
            "tickerData": {
                closeKeyString+"":closePrice,
                openKeyString+"":openPrice,
                highKeyString+"":highPrice,
                lowKeyString+"":lowPrice,
                volumeKeyString+"": volume
            },
            'lastThirtyMinSpans': lastThirtyMinSpanTicker
        }
        
        return retValue
    else:
        return None

def load_pre_time_series(symbol,
    downloadIfNotFound = True, precedingMinuteSpan = 15):

    folderPath = '..\\EstimateTrainingData\\StockDump\\'
    retValue = []
    allNamesIntraDay = getStockFileNames(symbol, 'TIME_SERIES_INTRADAY', folderPath=folderPath)
    allNamesSeriesDay = getStockFileNames(symbol, "TIME_SERIES_DAILY" , folderPath=folderPath)
    latestSeriesDailyFileName = "";
    jsonObj = "";

    intraDayKeys = list(allNamesIntraDay.keys())
    intraDayKeys.sort()

    seriesDayKeys = list(allNamesSeriesDay.keys())
    seriesDayKeys.sort()
    retValue = None

    if(len(intraDayKeys) > 0 and len(seriesDayKeys) > 0):
        lastIntraDayKey = intraDayKeys[len(intraDayKeys) - 1]
        lastSeriesDayKey = seriesDayKeys[len(seriesDayKeys) - 1]

        if(len(allNamesIntraDay) > 0):
            seriesDailyKeys = list(allNamesSeriesDay.keys())
            seriesDailyKeys = sorted(allNamesSeriesDay, reverse=True)
            seriesDayJsonFileName = None
            for fileName in seriesDailyKeys:
                namePathTuple = allNamesSeriesDay[fileName]
                latestSeriesDailyFileName = namePathTuple[0]
                seriesDayJsonFileName = namePathTuple[1]
                break

            intraDayKeys = list(allNamesIntraDay.keys())
            intraDayKeys = sorted(allNamesIntraDay, reverse=True)
            for fileName in intraDayKeys:
                namePathTuple = allNamesIntraDay[fileName]
                intraDayFileName = namePathTuple[0];
                intraDayJsonFileName = namePathTuple[1];
                break;

            #Read JSON data into the datastore variable
            if latestSeriesDailyFileName:
                with open(seriesDayJsonFileName, 'r') as f:
                    datastore = json.load(f)
                    seriesDailyJsonObj = datastore
            
            if seriesDailyJsonObj:
                timeSeries = seriesDailyJsonObj
                


            if intraDayFileName:
                with open(intraDayJsonFileName, 'r') as f:
                    datastore = json.load(f)
                    intraDayJsonObj = datastore
            
            if intraDayJsonObj:
                intraDaySeries = intraDayJsonObj
                eastern = pytz.timezone('America/New_York')
                now = datetime.datetime.now()
                now = eastern.localize(datetime.datetime(now.year, now.month, now.day, 15, 55, 0))
                
                marketClose = eastern.localize(datetime.datetime(now.year, now.month, now.day, 16, 0, 0))
                intraDayTickerDataSummary = getTimeSeriesFromIntraDaily(intraDaySeries, now, precedingMinuteSpan)
                lastThirtyMinSpanTicker = intraDayTickerDataSummary['lastThirtyMinSpans']
                if len(lastThirtyMinSpanTicker) > 1:
                    timeDelta = marketClose - now
                    extraPolateSpanInMs = (timeDelta.total_seconds() * 1000)
                    extraPolation = extrapolateClosingPrice(lastThirtyMinSpanTicker, extraPolateSpanInMs)
                    priceDelta = extraPolation['priceDelta']
                    intraDayTickerData = intraDayTickerDataSummary['tickerData']
                    openPrice = intraDayTickerData[currentStockTicker.open+""]
                    closePrice = intraDayTickerData[currentStockTicker.close+""]+priceDelta
                    highPriceSofar = intraDayTickerData[currentStockTicker.high+""]
                    lowPriceSofar = intraDayTickerData[currentStockTicker.low+""]

                    if closePrice > highPriceSofar:
                        highPriceSofar = closePrice
                    
                    if closePrice < lowPriceSofar:
                        lowPriceSofar = closePrice

                    nowAsString = now.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    intraDayTickerDataEstimation = {
                        'date': nowAsString,
                        'symbol': symbol,
                        currentStockTicker.close+"":closePrice,
                        currentStockTicker.open+"":openPrice,
                        currentStockTicker.high+"":highPriceSofar,
                        currentStockTicker.low+"":lowPriceSofar,
                        currentStockTicker.volume+"":68732872876,
                        "isExtrapolated":True
                    }
                    print (intraDayTickerDataEstimation);
                    timeSeries.append(intraDayTickerDataEstimation)
                
        timeSeriesTickerData = processTimeSeries_DayToStock(timeSeries)
        retValue = timeSeriesTickerData
        
    
    return retValue


def load_time_series_daily(
    symbol, 
    series_type = "TIME_SERIES_DAILY",
    downloadIfNotFound = True
    ):
    retValue = []
    allNames = getStockFileNames(symbol, series_type)
    latestFileName = "";
    jsonObj = "";

    if len(allNames) < 1 and downloadIfNotFound:
        downloadStockBySymbol(symbol, series_type)


    if(len(allNames) > 0):
        nameKeys = list(allNames.keys())
        nameKeys = sorted(allNames, reverse=True)
        for fileName in nameKeys:
            namePathTuple = allNames[fileName]
            latestFileName = namePathTuple[0];
            jsonFileName = namePathTuple[1];
            break;

        #Read JSON data into the datastore variable
        if latestFileName:
            with open(jsonFileName, 'r') as f:
                datastore = json.load(f)
                jsonObj = datastore
    
    if jsonObj:
        timeSeries = jsonObj
        # timeSeriesTickerData = processTimeSeries(timeSeries);
        timeSeriesTickerData = processTimeSeries_DayToStock(timeSeries);
        retValue = timeSeriesTickerData;
    
    return retValue;

# Funcition creates sequential time series data based on all riemseries dict
# Each time serie entry is open, lowPrice, HighPrice, ClosePrice

def processTimeSeries (timeSeriesDict):
    tickerData = [];
    keys = [];
    keys.extend(timeSeriesDict.keys());
    keys.sort();
    for key in keys:
        timeData = timeSeriesDict[key]
        # print ("open is " + timeData["1. open"])
        openPrice = float(timeData[currentStockTicker.open]);
        closePrice = float(timeData[currentStockTicker.close]);
        lowestPrice = float(timeData[currentStockTicker.low]);
        highstPrice = float(timeData[currentStockTicker.high]);
        tickerData.append(openPrice);
        tickerData.append(lowestPrice);
        tickerData.append(highstPrice);
        tickerData.append(closePrice);
    
    return tickerData;

def processTimeSeries_DayToStock(timeSeriesDict):
    '''
    function returns ticker data as a dictionary in which the key is number of days from 1970 Jan 1
    The value of the key is open, low, high, and close of the stock symbol. If it is tim series data this entry should be sorted by time
    '''
    closeKeyString = currentStockTicker.close
    openKeyString = currentStockTicker.open
    highKeyString = currentStockTicker.high
    lowKeyString = currentStockTicker.low
    volumeKeyString = currentStockTicker.volume
    tickerKey = "ticker";
    beginningOfTime_str = "1970-01-01 00:00:00";
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {}
    symbolData = {
        
    }

    allDayIndexes = set()
    bounds = {
        "min":None,
        "max":None,
    }
    for entry in timeSeriesDict:
        timeStr = entry['date']
        timeData = entry
        time = datetime.datetime.strptime(timeStr, '%Y-%m-%dT%H:%M:%S.%fZ')
        dayDiff = (time - beginningOfTime).days
        currentMin = bounds["min"]
        currentMax = bounds["max"]

        if currentMin is None or dayDiff < currentMin:
            currentMin = dayDiff
            bounds["min"] = currentMin

        if currentMax is None or currentMax < dayDiff:
            currentMax = dayDiff
            bounds["max"] = currentMax

        tickerData = []
        allDayIndexes.add(dayDiff);
        if dayDiff in symbolData:
            tickerData = symbolData[dayDiff][tickerKey]

        else:
            symbolData[dayDiff] = {
                ""+tickerKey+"": tickerData
            };
        openPrice = float(timeData[openKeyString]);
        lowestPrice = float(timeData[lowKeyString]);
        highstPrice = float(timeData[highKeyString]);
        closePrice = float(timeData[closeKeyString]);
        volume = float(timeData[volumeKeyString]);
        avgPrice = (closePrice + openPrice)/2
        
        # DO NOT CHANGE THE APPEND ORDER 
        tickerData.append(openPrice);#0
        tickerData.append(lowestPrice);#1
        tickerData.append(highstPrice);#2
        tickerData.append(closePrice);#3
        tickerData.append(avgPrice);#4
        tickerData.append(volume);#5
        
    # symbolData["allDayIndexes"] = allDayIndexes
    # symbolData["dayBounds"] = bounds
    dayIndexList = list(allDayIndexes)
    dayIndexList.sort()
    dayIndexToListIndex = {}
    indexCounter = 0
    for dayIndex in dayIndexList:
        dayIndexToListIndex[dayIndex] = indexCounter
        indexCounter+=1
    retValue["symbolData"] = symbolData
    retValue["dayBounds"] = bounds
    retValue["allDayIndexes"] = allDayIndexes
    retValue["formatedIndexes"] = {
        'dayIndexToListIndex': dayIndexToListIndex,
        'orderedDayIndex': dayIndexList,
        'allDayIndexes': allDayIndexes
    }
    return retValue;
