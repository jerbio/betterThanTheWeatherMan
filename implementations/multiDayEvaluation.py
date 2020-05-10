import datetime
import tensorflow as tf

class WeatherManPredictionTestConfig:
    def __init__(self): 
        self.epochCount = 100
        self.daysPerYear = 365
        self.percentageDeltaChange = 1
        self.testRatio = 0.3
        self.numberOfTrainingWindowDays = 90
        self.numberOfOutlookDays = 4 # The number of days to check if ther was sufficient percentage_delta_lift in the training delta set
        self.modelRebuildCount = 1 # this is the number of retry model builds. This then picks the model with the best acuracy
        self.numberOfDaysBeforeRetrainingModel = 2 # After this number days of prediction we'll need to rebuild model to prevent the model from losing its potency
        self.numberOfRetroDays = 120 # Number of fays from the past of a predictiona day to pull or build features
        self.earliestTimeInYearsFromToday = 1 # this is the earliest dayindex from which you'll use for training
        self.numberOfDaysForTraining = 90 # this is the last day after earliestTimeInYearsFromToday which you'll use for training the model
        self.stockPerDay = 2 # Number of stocks to predict per day of prediction

    def printMe(self):
        retValue =f'''
        epoch count: {self.epochCount}
        daysPerYear: {self.daysPerYear}
        percentageDeltaChange: {self.percentageDeltaChange}%
        testRatio: {self.testRatio}
        numberOfTrainingWindowDays: {self.numberOfTrainingWindowDays}
        numberOfOutlookDays: {self.numberOfOutlookDays}
        modelRebuildCount: {self.modelRebuildCount}
        numberOfDaysBeforeRetrainingModel: {self.numberOfDaysBeforeRetrainingModel}
        numberOfRetroDays: {self.numberOfRetroDays}
        earliestTimeInYearsFromToday: {self.earliestTimeInYearsFromToday}
        numberOfDaysForTraining: {self.numberOfDaysForTraining}
        stockPerDay: {self.stockPerDay}
        '''
        print(retValue)

        


