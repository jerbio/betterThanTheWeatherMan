import requests 
import os
import errno
from datetime import datetime, timedelta
import time
from pathlib import Path
from ..weatherutility import dayIndexFromStart, timeFromDayIndex

time_fmt = '%m-%d-%y %H:%M:%S'
requestBatches = [];
timeOfRequest = str(Path("temp/lastBatch.txt")) 
requestPerMinute = 5;
currentRequestCount = 0;
oneMinuteInSeconds = 60
downloadConfig = None;
defaultSymbol = "MSFT";

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

def getApiKey():
    return 'apikey'



def getDownloadConfig(series_type, datatype):
    global downloadConfig
    
    PARAMS = {
        'function':series_type,
        'symbol':defaultSymbol,
        'apikey':None,
        'datatype': datatype,
        'interval': None,
        'outputsize':'full'
    }

    def getSampleFoloderstr(Path():
        retValue = str(Path("../TrainingData/StockDump/WEATHERSAMPLE_00000/"+series_type))
        return retValue

    def initializeDownloadCoinfg():
        global downloadConfig
        walk = os.walk
        # series_type = "TIME_SERIES_DAILY";
        dirname = os.path.dirname(__file__)
        retValue = {}

        fullFolderPath = getSampleFoloderstr(Path()
        walkedFileNames = []
        for (dirpath, dirnames, filenames) in walk(fullFolderPath):
            for fileName in filenames:
                walkedFileNames.append(fileName)
        
        walkedFileNames = sorted(walkedFileNames, reverse=True)
        latestFileName = walkedFileNames[0]
        dateString = latestFileName[:10]
        fileDayDate = datetime.datetime.strptime(dateString, '%Y-%m-%d')
        dayIndex = dayIndexFromStart(fileDayDate)
        downloadConfig ={
            "currentDayIndex": dayIndex,
            "dateString": dateString,
            "fileName": latestFileName,
            "folderString": dateString
        }


    def isConfigLatest():
        retValue = False
        downloadConfig = {}
        if downloadConfig is not None:
            configDayIndex = downloadConfig["currentDayIndex"]
            beginningOfTime_str = "1970-01-01 00:00:00"
            beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
            currentDayIndex = int((time - beginningOfTime).days)
            retValue = currentDayIndex == configDayIndex

        return retValue

    

    if isConfigLatest() == False:
        folderPath = getSampleFoloderstr(Path()
        batchRequests(PARAMS, folderPath, True)
        initializeDownloadCoinfg()
    
    return downloadConfig


def downloadStockBySymbol (
    symbol = "MSFT",
    series_type = "TIME_SERIES_DAILY",
    filePath = "",
    ignoreIfExists = False
    ):
    dirname = os.path.dirname(__file__)

    datatype = "json"
    PARAMS = {
        'function':series_type,
        'symbol':symbol,
        'apikey':None,
        'datatype': datatype,
        'interval': None,
        'outputsize':'full'
    }
    if filePath:
         folderPath = filePath
    else:
        downloadConfig = getDownloadConfig(series_type, datatype)
        folderString = downloadConfig["folderString"]
        folderPath = str(Path("../TrainingData/StockDump/"+folderString))

    fullFolderPath = str(Path(folderPath +"/"+ series_type+"/"+symbol))

    pathLookup = filePath if filePath else os.path.join(dirname, fullFolderPath)
    if ignoreIfExists and os.path.exists(pathLookup):
        print("Not downloading "+symbol+" because already exists" )
        return

    batchRequests(PARAMS, fullFolderPath)


    
    
def groupSymbolRequest(
    symbols,
    series_type = "TIME_SERIES_DAILY",
    filePath = "",
    ignoreIfExists = False
    ):
    for symbol in symbols:
        downloadStockBySymbol(symbol, series_type, filePath, ignoreIfExists)



def batchRequests(PARAMS, fullFolderPath, isSample = False):
    now = datetime.now()
    api_key = "SDXP9BXB3745PKEB"
    
    interval = "30min"

    PARAMS ['apikey'] = api_key
    PARAMS ['interval'] = interval
    

    lastEntry = getTimeOfLastRequest()
    print("Last update is ", lastEntry)
    global currentRequestCount
    global requestPerMinute
    print("Current request count ", currentRequestCount)

    if (
            (currentRequestCount<requestPerMinute) and 
            ((not lastEntry) or (((now - lastEntry) > timedelta(seconds=oneMinuteInSeconds))))
        ):
        sendRequests(PARAMS, fullFolderPath)
        currentRequestCount += 1
    else:
        print("Sleeping for next "+str(oneMinuteInSeconds)+" seconds")
        updateLastBatchRequest()
        time.sleep(oneMinuteInSeconds)
        sendRequests(PARAMS, fullFolderPath)
        currentRequestCount = 1

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
    fullFilePath = str(Path(folderPath+"/"+dateOfQuery+".json"));
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