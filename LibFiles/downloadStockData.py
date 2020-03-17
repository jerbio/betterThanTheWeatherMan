import requests 
import os
import errno


def downloadStockBySymbol (
    symbol = "MSFT",
    series_type = "TIME_SERIES_DAILY"
    ):
    dirname = os.path.dirname(__file__)

    api_key = "SDXP9BXB3745PKEB"
    datatype = "json"
    interval = "30min"

    # api-endpoint 
    # URL = "https://www.alphavantage.co/query?function="+series_type+"&symbol="+symbol+"&interval=5min&apikey="+api_key
    URL = "https://www.alphavantage.co/query"

    PARAMS = {
        'function':series_type,
        'symbol':symbol,
        'apikey':api_key,
        'datatype': datatype,
        'interval': interval,
        'outputsize':'full'
    }

    r = requests.get(url = URL, params = PARAMS)
    jsonResult = r.json()

    timeOfQuery = jsonResult["Meta Data"]["3. Last Refreshed"]
    dateOfQuery = timeOfQuery.split()[0]

    fullFilePath = "..\\TrainingData\\StockDump\\"+series_type+"\\"+symbol+"\\"+dateOfQuery+".json"
    filename = os.path.join(dirname, fullFilePath)


    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    f = open(filename, "w")
    f.write(r.text)