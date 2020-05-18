import requests 
import os
import errno
from datetime import datetime, timedelta
import time

time_fmt = '%m-%d-%y %H:%M:%S'
requestBatches = [];
timeOfRequest = "temp/lastBatch.txt"
requestPerMinute = 5;
currentRequestCount = 0;
oneMinuteInSeconds = 60

def getTimeOfLastRequest():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, timeOfRequest)
    f = open(filename, "r")
    currentTimeStr = f.read();
    now = datetime.now();
    retValue = None;
    if currentTimeStr:
        retValue = datetime.strptime(currentTimeStr, time_fmt)
    return retValue;

def updateLastBatchRequest():
    dirname = os.path.dirname(__file__)
    now = datetime.now();
    currentTime = now.strftime(time_fmt);

    filename = os.path.join(dirname, timeOfRequest)

    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    
    f = open(filename, "w");
    f.write(currentTime);
    f.close()



def downloadStockBySymbol (
    symbol = "MSFT",
    series_type = "TIME_SERIES_DAILY",
    filePath = "",
    ignoreIfExists = False
    ):
    dirname = os.path.dirname(__file__)


    api_key = "SDXP9BXB3745PKEB"
    datatype = "json"
    interval = "30min"
    PARAMS = {
        'function':series_type,
        'symbol':symbol,
        'apikey':api_key,
        'datatype': datatype,
        'interval': interval,
        'outputsize':'full'
    }
    folderPath = filePath if filePath  else "..\\TrainingData\\StockDump";

    now = datetime.now();

    fullFolderPath = folderPath +"\\"+ series_type+"\\"+symbol;

    pathLookup = filePath if filePath else os.path.join(dirname, fullFolderPath)
    if os.path.exists(pathLookup):
        filesInPath = []
        walk = os.walk
        for (dirpath, dirnames, filenames) in walk(pathLookup):
            for fileName in filenames:
                filesInPath.append(fileName)
        if ignoreIfExists and len(filesInPath) > 0:
            print("Not downloading "+symbol+" because already exists" )
            return

    lastEntry = getTimeOfLastRequest();
    print("Last update is ", lastEntry)
    global currentRequestCount;
    global requestPerMinute;
    print("Current request count ", currentRequestCount)

    if (
            (currentRequestCount<requestPerMinute) and 
            ((not lastEntry) or (((now - lastEntry) > timedelta(seconds=oneMinuteInSeconds))))
        ):
        sendRequests(PARAMS, fullFolderPath)
        currentRequestCount += 1;
    else:
        print("Sleeping for next "+str(oneMinuteInSeconds)+" seconds");
        updateLastBatchRequest();
        time.sleep(oneMinuteInSeconds);
        sendRequests(PARAMS, fullFolderPath)
        currentRequestCount = 1;

    
    
def groupSymbolRequest(
    symbols,
    series_type = "TIME_SERIES_DAILY",
    filePath = "",
    dontDownloadIfExists = False
    ):
    for symbol in symbols:
        downloadStockBySymbol(symbol, series_type, filePath, dontDownloadIfExists)


def sendRequests(PARAMS, folderPath):
    dirname = os.path.dirname(__file__)
    symbol = PARAMS["symbol"]
    series_type = PARAMS["function"]



    # api-endpoint 
    # URL = "https://www.alphavantage.co/query?function="+series_type+"&symbol="+symbol+"&interval=5min&apikey="+api_key
    URL = "https://www.alphavantage.co/query"

    print('retrieving for ' +symbol+ "\n\tseries_type " + series_type);
    r = requests.get(url = URL, params = PARAMS)
    jsonResult = r.json();

    metaData = jsonResult["Meta Data"]
    timeOfQuery = metaData["3. Last Refreshed"];
    dateOfQuery = timeOfQuery.split()[0]
    fullFilePath = folderPath+"\\"+dateOfQuery+".json";
    print ("saving to ", fullFilePath)
    filename = os.path.join(dirname, fullFilePath)


    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    f = open(filename, "w")
    f.write(r.text)