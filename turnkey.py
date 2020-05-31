import datetime
import os
import errno
import json
import tensorflow as tf
import numpy



from weatherutility import dayIndexFromStart, timeFromDayIndex

# from .weatherutility import dayIndexFromStart
from implementations.weathermanpredictionconfig import WeatherManPredictionConfig
from implementations.onlypositivedeltas import getAllTrainingPiecesPreClosing, getAllTrainingPieces, getBestModel, getStockSuggestionSymbolToData, convertTickerForPrediction, predict


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, float):
            return str(obj)
        if isinstance(obj, numpy.float32):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def turnTheKey(config:WeatherManPredictionConfig, tickerSymbols, isAuto = True):
    model = loadLatestModel(config, isAuto)
    retryCountLimit = 4
    retryCount = 0

    config.stockPerDay = 3

    predictionStartTime = datetime.datetime.now()
    predictionDayIndex = dayIndexFromStart(predictionStartTime)

    parameters = getAllTrainingPiecesPreClosing(config, tickerSymbols)
    allSymbolsToTickerData = parameters["allSymbolsToTickerData"]
    dataIndexToSymbol = parameters["dataIndexToSymbol"]
    allDayIndexes = parameters["dayIndexes"]

    while predictionDayIndex not in allDayIndexes and retryCount < retryCountLimit:
        predictionDayIndex -= 1
        retryCount += 1
    
    if predictionDayIndex in allDayIndexes:
        symbolToDayData = getStockSuggestionSymbolToData(config, allSymbolsToTickerData, predictionDayIndex)
    
        predictionData = convertTickerForPrediction(symbolToDayData)
        stockData = predictionData['symbolData']
        featureLengthPerRetroDay = predictionData['featureLengthPerRetroDay']
        stockResult = predict(config, model, dataIndexToSymbol, stockData, featureLengthPerRetroDay)
        if(len(stockResult) > 0):
            print ("Done analyzing you should buy the stocks below:")
            print(stockResult)
            currentTime = datetime.datetime.now()
            timeString = currentTime.strftime('%Y_%m_%dT%H_%M_%S_%fZ')
            predictionFolderPath = config.predictionFolder
            if isAuto:
                predictionFolderPath = config.predictionFolderTurnedKey
            predictionFolderPath += '\\prediction_'+ timeString +''

            predictionFileName = 'prediction.json'
            predictionFileNamePath = predictionFolderPath+'\\'+predictionFileName

            if not os.path.exists(os.path.dirname(predictionFileNamePath)):
                try:
                    os.makedirs(os.path.dirname(predictionFileNamePath))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            with open(predictionFileNamePath, 'w') as outfile:
                json.dump(stockResult, outfile, cls=SetEncoder, indent=4)

        else: 
            print ("\n\n\nSorry bro, no stock buying today")
    else:
        print ("Cannot predict stock because the time provided is not within")


def loadLatestModel(config:WeatherManPredictionConfig, isAuto = False):
    modelFolder = config.modelFolderPath
    if isAuto:
        modelFolder = config.modelFolderPathTurnedKey
    folderPaths = {}
    walk = os.walk;
    for (dirpath, dirnames, fileNames) in walk(modelFolder):
        for folderPath in dirnames:
            fullFolderName = modelFolder+folderPath;
            folderPaths[folderPath] = (folderPath, fullFolderName);
        break;
    

    modelFolderNames = list(folderPaths.keys())
    modelFolderNames.sort()
    latestFolderName = modelFolderNames[len(modelFolderNames) - 1]

    modelFileName = 'model'
    modelFileNamePath = modelFolder+'\\'+latestFolderName+'\\'+modelFileName
    retValue = tf.keras.models.load_model(modelFileNamePath)
    retValue.summary()
    return retValue


def generateModel(config:WeatherManPredictionConfig, tickerSymbols, isAuto = False):
    config.epochCount = 200
    config.modelRebuildCount = 3
    config.stockPerDay = 3
    currentTime = datetime.datetime.now()
    config.printMe()
        
    earliestTime = currentTime + datetime.timedelta(days=(-180))
    finalTime = currentTime #+ datetime.timedelta(days=())

    

    print ("We are about to generate a model on "+str(finalTime))

    parameters = getAllTrainingPieces(config, tickerSymbols)
    allSymbolsToTickerData = parameters["allSymbolsToTickerData"]
    dataIndexToSymbol = parameters["dataIndexToSymbol"]
    allDayIndexes = parameters["dayIndexes"]

    trainingStartTIme = earliestTime
    trainingEndTime = finalTime + datetime.timedelta(days=(-config.numberOfOutlookDays))
    model = getBestModel(config, allSymbolsToTickerData, dataIndexToSymbol, trainingStartTIme, trainingEndTime)["model"]
    predictionStartTime = finalTime
    predictionDayIndex = dayIndexFromStart(predictionStartTime)
    timeString = currentTime.strftime('%Y_%m_%dT%H_%M_%S_%fZ')
    modelFolderPath = config.modelFolderPath
    if isAuto:
        modelFolderPath = config.modelFolderPathTurnedKey
    modelFolderPath += '\\model_'+ timeString +''

    modelConfig = {
        'symbols': tickerSymbols
    }

    configSetUpFileName = 'config.json'
    configFileNamePath = modelFolderPath+'\\'+configSetUpFileName
    # jsonObj = json.dumps(modelConfig, cls=SetEncoder, indent = 4) 

    if not os.path.exists(os.path.dirname(configFileNamePath)):
        try:
            os.makedirs(os.path.dirname(configFileNamePath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(configFileNamePath, 'w') as outfile:
        json.dump(modelConfig, outfile)


    symbolDataFileName = 'symbolData.json'
    symbolDataFileNamePath = modelFolderPath+'\\'+symbolDataFileName
    # allSymbolsJsonObj = json.dumps(allSymbolsToTickerData, cls=SetEncoder, indent = 4) 
    if not os.path.exists(os.path.dirname(symbolDataFileNamePath)):
        try:
            os.makedirs(os.path.dirname(symbolDataFileNamePath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(symbolDataFileNamePath, 'w') as outfile:
        json.dump(allSymbolsToTickerData, outfile, cls=SetEncoder, indent=4)
    
    modelFileName = 'model'
    modelFileNamePath = modelFolderPath+'\\'+modelFileName
    model.save(modelFileNamePath)


