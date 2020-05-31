import requests 
import os
import errno
from datetime import datetime, timedelta
import time
import threading


time_fmt = '%m-%d-%y %H:%M:%S'
requestBatches = [];
timeOfRequest = "temp/lastBatch.txt"
requestPerMinute = 20000
currentRequestCount = 0
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


    api_key = "6f2218f24b0b8bfebf06b0cb11475563db9fa720"
    datatype = "json"
    interval = "5min"
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
        if 'INTRA' in series_type:
            sendIntraDayRequest(PARAMS, fullFolderPath)
        else:
            sendDailyRequests(PARAMS, fullFolderPath)
        currentRequestCount += 1;
    else:
        print("Sleeping for next "+str(oneMinuteInSeconds)+" seconds");
        updateLastBatchRequest();
        time.sleep(oneMinuteInSeconds);
        if 'INTRA' in series_type:
            sendIntraDayRequest(PARAMS, fullFolderPath)
        else:
            sendDailyRequests(PARAMS, fullFolderPath)
        currentRequestCount = 1;


class downloadStockThread (threading.Thread):
   def __init__(self, threadID, name, symbol, series_type, filePath, dontDownloadIfExists):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.symbol = symbol
      self.series_type = series_type
      self.filePath = filePath
      self.dontDownloadIfExists = dontDownloadIfExists
   def run(self):
      print ("Starting " + self.name)
      downloadStockBySymbol(self.symbol, self.series_type, self.filePath, self.dontDownloadIfExists)
      print( "Exiting " + self.name)
    
    
def groupSymbolRequest(
    symbols,
    series_type = "TIME_SERIES_DAILY",
    filePath = "",
    dontDownloadIfExists = False,
    isMultiThreaded = False
    ):
    if not isMultiThreaded:
        for symbol in symbols:
            downloadStockBySymbol(symbol, series_type, filePath, dontDownloadIfExists)
    else:
        threadCounter = 0
        threads = []
        for symbol in symbols:
            threadName = 'symbol - '+ str(threadCounter) + ' - ' + symbol
            dowloadThread = downloadStockThread(threadCounter, threadName, symbol, series_type, filePath, dontDownloadIfExists)
            dowloadThread.start()
            threads.append(dowloadThread)
            # downloadStockBySymbol(symbol, series_type, filePath, dontDownloadIfExists)
            threadCounter+=1
            if (threadCounter)% 20 == 19:
                time.sleep(3)

def sendIntraDayRequest(PARAMS, folderPath):
    dirname = os.path.dirname(__file__)
    symbol = PARAMS["symbol"]
    dateAsString = datetime.today().strftime("%Y-%m-%d")
    relevantParams = {
        'token': PARAMS['apikey'],
        'resampleFreq': PARAMS['interval'],
        'startDate': dateAsString
    }
    headers = {
    'Content-Type': 'application/json'
    }


    # api-endpoint 
    URL = "https://api.tiingo.com/iex/"+symbol+'/prices'

    print('retrieving for ' +symbol+ "\n\tseries_type is TIME_SERIES_INTRADAY");
    r = requests.get(url = URL, params = relevantParams, headers=headers)
    jsonResult = r.json();
    
    if(len(jsonResult) > 0):
        lastEntry = jsonResult[len(jsonResult) - 1]
        dateString = lastEntry['date']
        dateObject = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S.%fZ')
        dateAsString = dateObject.strftime("%Y-%m-%d")
        fullFilePath = folderPath+"\\"+dateAsString+".json";
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
    else:
        print('Failed to PRINT for the config '+ str(PARAMS))

def sendDailyRequests(PARAMS, folderPath):
    dirname = os.path.dirname(__file__)
    symbol = PARAMS["symbol"]

    relevantParams = {
        'token': PARAMS['apikey'],
        # 'resampleFreq': PARAMS['5min'],
        'startDate': '1970-01-01'
    }
    headers = {
    'Content-Type': 'application/json'
    }


    # api-endpoint 
    URL = "https://api.tiingo.com/tiingo/daily/"+symbol+'/prices'

    print('retrieving for ' +symbol+ "\n\tseries_type is TIME SERIES DAILY");
    r = requests.get(url = URL, params = relevantParams, headers=headers)
    jsonResult = r.json();
    
    if(len(jsonResult) > 0):
        lastEntry = jsonResult[len(jsonResult) - 1]
        dateString = lastEntry['date']
        dateObject = datetime.strptime(dateString, '%Y-%m-%dT%H:%M:%S.%fZ')
        dateAsString = dateObject.strftime("%Y-%m-%d")
        fullFilePath = folderPath+"\\"+dateAsString+".json";
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
    else:
        print('Failed to PRINT for the config '+ str(PARAMS))

    


def main(symbol):
    # key = "_1_ortWykxsLQvPQk2eIV3jmfk5_3e5tuzq_AN"
    # client = RESTClient(key)

    # resp = client.stocks_equities_daily_open_close("AAPL", "2018-3-2")
    # print(f"On: {resp.from_} Apple opened at {resp.open} and closed at {resp.close}")

    headers = {
    'Content-Type': 'application/json'
    }
    requestResponse = requests.get("https://api.tiingo.com/iex/"+symbol+"/prices?startDate=2020-05-22&resampleFreq=5min&token=9d5ddc8e9e13f8b1d800c55a6bdeefb8ff10cd79", headers=headers)
    # requestResponse = requests.get("https://api.tiingo.com/tiingo/daily/"+symbol+"/prices?startDate=1970-01-01&token=9d5ddc8e9e13f8b1d800c55a6bdeefb8ff10cd79", headers=headers)
    print(requestResponse.json())

main('TOTAU')