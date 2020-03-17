import os
import json

def load_time_series_daily(
    symbol
    ):
    walk = os.walk;
    series_type = "TIME_SERIES_DAILY";
    dirname = os.path.dirname(__file__)
    retValue = [];

    fullFolderPath = "..\\TrainingData\\StockDump\\"+series_type+"\\"+symbol+"\\";
    allNames = []
    for (dirpath, dirnames, filenames) in walk(fullFolderPath):
        allNames.extend(filenames)

    allNames.sort()
    latestFileName = "";
    jsonObj = "";
    if(len(allNames) > 0):
        latestFileName = allNames[len(allNames) - 1];
        jsonFileName = fullFolderPath+latestFileName;

        #Read JSON data into the datastore variable
        if latestFileName:
            with open(jsonFileName, 'r') as f:
                datastore = json.load(f)
                jsonObj = datastore
    
    if jsonObj:
        timeSeries = jsonObj["Time Series (Daily)"];
        timeSeriesTickerData = processTImeSeries(timeSeries);
        retValue = timeSeriesTickerData;
    
    return retValue;

# Funcition creates sequential time series data based on all riemseries dict
# Each time serie entry is open, lowPrice, HighPrice, ClosePrice

def processTImeSeries (timeSeriesDict):
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
    print (keys)

    # print (allNames)
