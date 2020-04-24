import os
import json
import datetime
from .downloadstockdata import downloadStockBySymbol

def getStockFileNames(symbol, series_type):
    walk = os.walk;
    # series_type = "TIME_SERIES_DAILY";
    dirname = os.path.dirname(__file__)
    retValue = {};

    fullFolderPath = "..\\TrainingData\\StockDump\\"+series_type+"\\"+symbol+"\\";
    pathFoFolder = dirname+"\\..\\TrainingData\\StockDump\\"+series_type+"\\"+symbol+"\\";
    fullFolderPath = pathFoFolder
    for (dirpath, dirnames, filenames) in walk(fullFolderPath):
        for fileName in filenames:
            fullFileName = fullFolderPath+fileName;
            retValue[fileName] = (fileName, fullFileName);
    
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
        for fileName in allNames:
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
        timeSeries = jsonObj["Time Series (Daily)"];
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
        openPrice = float(timeData["1. open"]);
        closePrice = float(timeData["4. close"]);
        lowestPrice = float(timeData["3. low"]);
        highstPrice = float(timeData["2. high"]);
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
    tickerKey = "ticker";
    beginningOfTime_str = "1970-01-01 00:00:00";
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = {
        
    }


    for entry in timeSeriesDict:
        timeStr = entry;
        timeData = timeSeriesDict[entry];
        time = datetime.datetime.strptime(timeStr, '%Y-%m-%d')
        dayDiff = (time - beginningOfTime).days

        tickerData = []
        if dayDiff in retValue:
            tickerData = retValue[dayDiff][tickerKey]

        else:
            retValue[dayDiff] = {
                ""+tickerKey+"": tickerData
            };
        openPrice = float(timeData["1. open"]);
        closePrice = float(timeData["4. close"]);
        lowestPrice = float(timeData["3. low"]);
        highstPrice = float(timeData["2. high"]);
        tickerData.append(openPrice);
        tickerData.append(lowestPrice);
        tickerData.append(highstPrice);
        tickerData.append(closePrice);
    
    return retValue;
