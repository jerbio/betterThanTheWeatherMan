import datetime
import os
import sys
import errno
import json
import tensorflow as tf
import numpy
from pathlib import Path

PACKAGE_PARENT = '../../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
PACKAGE_PARENT = '../'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from weatherutility import dayIndexFromTime, timeFromDayIndex, getDayIndexes

# from .weatherutility import dayIndexFromTime
from weathermanpredictionconfig import WeatherManPredictionConfig
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


    predictionStartTime = datetime.datetime.now()
    predictionDayIndex = dayIndexFromTime(predictionStartTime)

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
            for stockPrediction in stockResult:
                stockSymbol = stockPrediction['symbol']
                if 'extrapolatedTicker' in allSymbolsToTickerData[stockSymbol]:
                    lengthOfExtraPolations = len(allSymbolsToTickerData[stockSymbol]['extrapolatedTicker'])
                    projectedClosingPrice = allSymbolsToTickerData[stockSymbol]['extrapolatedTicker'][lengthOfExtraPolations -1][3]
                    stockPrediction['dayIndex'] = allSymbolsToTickerData[stockSymbol]['extrapolatedTicker'][lengthOfExtraPolations -1][7]
                    stockPrediction['extrapolatedClosingPrice'] = projectedClosingPrice
                    stockPrediction['extrapolatedTicker'] = allSymbolsToTickerData[stockSymbol]['extrapolatedTicker'][lengthOfExtraPolations -1]
                    
            currentTime = datetime.datetime.now()
            timeString = currentTime.strftime('%Y_%m_%dT%H_%M_%S_%fZ')
            predictionFolderPath = config.predictionFolder()
            if isAuto:
                predictionFolderPath = config.predictionFolderTurnedKey()
            predictionFolderPath += '/prediction_'+ timeString +''

            predictionFileName = 'prediction.json'
            predictionFileNamePath = str(Path(predictionFolderPath+'/'+predictionFileName))

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
    modelFolder = config.modelFolderPath()
    if isAuto:
        modelFolder = config.modelFolderPathTurnedKey()
    folderPaths = {}
    walk = os.walk;
    for (dirpath, dirnames, fileNames) in walk(modelFolder):
        for folderPath in dirnames:
            fullFolderName = modelFolder+'/'+folderPath;
            folderPaths[folderPath] = (folderPath, fullFolderName);
        break;
    

    modelFolderNames = list(folderPaths.keys())
    modelFolderNames.sort()
    latestFolderName = modelFolderNames[len(modelFolderNames) - 1]

    modelFileName = 'model'
    modelFileNamePath = str(Path(modelFolder+'/'+latestFolderName+'/'+modelFileName))
    print("Loading model from  model to path "+ str(modelFileNamePath))
    retValue = tf.keras.models.load_model(modelFileNamePath)
    retValue.summary()
    return retValue


def generateModel(config:WeatherManPredictionConfig, tickerSymbols, isAuto = False):
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
    trainingEndTime = finalTime + datetime.timedelta(days=(-config.numberOfDaysWithPossibleResult))
    predictionDayStartDayIndex = dayIndexFromTime(trainingEndTime)
    if predictionDayStartDayIndex not in allDayIndexes:
        while predictionDayStartDayIndex not in allDayIndexes:
            predictionDayStartDayIndex -= 1
        trainingEndTime = timeFromDayIndex(predictionDayStartDayIndex)
    
    stockDataWithinWindow = []
    for symbol in allSymbolsToTickerData:
        if predictionDayStartDayIndex in allSymbolsToTickerData[symbol]['symbolData']:
            stockDataWithinWindow.append((symbol, allSymbolsToTickerData[symbol]['symbolData'][predictionDayStartDayIndex]['ticker'][4]))

    sortedSymbolDataByPrice = sorted(stockDataWithinWindow, key=lambda dayData: dayData[1], reverse= config.highValueStocks)[:50]

    windowSymbolData = {}
    for symbolAndPrice in sortedSymbolDataByPrice:
        windowSymbolData[symbolAndPrice[0]] = allSymbolsToTickerData[symbolAndPrice[0]]


    model = getBestModel(config, windowSymbolData, dataIndexToSymbol, trainingStartTIme, trainingEndTime)["model"]
    predictionStartTime = finalTime
    predictionDayIndex = dayIndexFromTime(predictionStartTime)
    timeString = currentTime.strftime('%Y_%m_%dT%H_%M_%S_%fZ')
    modelFolderPath = config.modelFolderPath()
    if isAuto:
        modelFolderPath = config.modelFolderPathTurnedKey()
    modelFolderPath += '/model_'+ timeString +''

    modelConfig = {
        'symbols': tickerSymbols
    }

    configSetUpFileName = 'config.json'
    configFileNamePath = str(Path(modelFolderPath+'/'+configSetUpFileName))
    # jsonObj = json.dumps(modelConfig, cls=SetEncoder, indent = 4) 

    if not os.path.exists(os.path.dirname(configFileNamePath)):
        try:
            os.makedirs(os.path.dirname(configFileNamePath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    print("Writing model to path "+ str(configFileNamePath))
    with open(configFileNamePath, 'w') as outfile:
        json.dump(modelConfig, outfile)


    symbolDataFileName = 'symbolData.json'
    symbolDataFileNamePath = str(Path(modelFolderPath+'/'+symbolDataFileName))
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
    modelFileNamePath = str(Path(modelFolderPath+'/'+modelFileName))
    model.save(modelFileNamePath)


