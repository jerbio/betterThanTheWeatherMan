import datetime
import tensorflow as tf

class WeatherManPredictionConfig:
    def __init__(self): 
        self.id = ''
        self.epochCount = 200
        self.daysPerYear = 365
        self.percentageDeltaChange = 3
        self.testRatio = 0.3
        self.numberOfDaysWithPossibleResult = 7 # The number of days to check if ther was sufficient percentage_delta_lift in the training delta set
        self.modelRebuildCount = 3 # this is the number of retry model builds. This then picks the model with the best acuracy
        self.numberOfDaysBeforeRetrainingModel = 2 # After this number days of prediction we'll need to rebuild model to prevent the model from losing its potency
        self.numberOfRetroDays = 120 # Number of days from the past of a prediction day to pull or build features
        self.earliestTimeInYearsFromToday = 1 # this is the earliest dayindex from which you'll use for training
        self.numberOfDaysForTraining = 90 # this is the last day after earliestTimeInYearsFromToday which you'll use for training the model
        self.stockPerDay = 2 # Number of stocks to predict per day of prediction
        self.rollingWindow = 12
        self.iterationNotes = ""
        self.threshold = 0.95
        self.dropout = 0.0
        self.previousDayDeltaCutoff = -2
        self.highValueStocks = False
        self.allowInflectionPoints = False
        self.allowOtherDayFeatures = True
        self.category = 'tech'
        self.exchange = 'nasdaq'
        
        
        self.preClosingMinuteSpan = 15 # The number of minutes from 'now' that'll be used to exrapolate the closing price. Assuming the curent time is currently 2:30p and this property is set to 15 min this till select ticker data between 2:15p and 2:30p to extrapolate the closing price
        self.isOverSampled = False

    def modelFolderPath(self):
        return './savedmodels'+'/'+self.category+'/'+self.exchange

    def modelFolderPathTurnedKey(self):
        return self.modelFolderPath() + '/lightningStrikes'

    def predictionFolder(self):
        return './predictionDump'+'/'+self.category+'/'+self.exchange

    def predictionFolderTurnedKey(self):
        return self.predictionFolder() + '/lightningStrikes'

    def printMe(self):
        retValue =f'''
        epoch count: {self.epochCount}
        daysPerYear: {self.daysPerYear}
        stockCategory = {self.category}
        exchange = {self.exchange}
        percentageDeltaChange: {self.percentageDeltaChange}
        testRatio: {self.testRatio}
        numberOfDaysWithPossibleResult: {self.numberOfDaysWithPossibleResult}
        modelRebuildCount: {self.modelRebuildCount}
        numberOfDaysBeforeRetrainingModel: {self.numberOfDaysBeforeRetrainingModel}
        numberOfRetroDays: {self.numberOfRetroDays}
        earliestTimeInYearsFromToday: {self.earliestTimeInYearsFromToday}
        numberOfDaysForTraining: {self.numberOfDaysForTraining}
        stockPerDay: {self.stockPerDay}
        dropout = {self.dropout}
        rollingWindow: {self.rollingWindow}
        threshold = {self.threshold}
        iterationNotes: {self.iterationNotes}
        previousDayDeltaCutoff: {self.previousDayDeltaCutoff}
        preClosingMinuteSpan: {self.preClosingMinuteSpan}
        modelFolderPath: {self.modelFolderPath()}
        modelFolderPathTurnedKey: {self.modelFolderPathTurnedKey()}
        predictionFolder: {self.predictionFolder()}
        predictionFolderTurnedKey: {self.predictionFolderTurnedKey()}
        allowInflectionPoints: {self.allowInflectionPoints}
        allowOtherDayFeatures: {self.allowOtherDayFeatures}
        highValueStocks: {self.highValueStocks}
        isOverSampled: {self.isOverSampled}
        '''
        print(retValue)

        


