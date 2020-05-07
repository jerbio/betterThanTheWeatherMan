import datetime
import tensorflow as tf

class WeatherManPredictionTestConfig:
    daysPerYear = 365
    percentage_delta_lift = 1
    numberOfTestDays = 1
    modelRebuildCount = 5 # this is the number of retry model builds. This then picks the model with the best acuracy
    numberOfDaysBeforeRetrainingModel = 7 # After this number days of prediction we'll need to rebuild model to prevent the model from losing its potency
    numberOfRetroDays = 120 # Number of fays from the past of a predictiona day to pull or build features
    numberOfDaysForTraining = 180 # this is the last day after earliestTimeInYearsFromToday which you'll use for training the model
    earliestTimeInYearsFromToday = 1 # this is the earliest dayindex from which you'll use for training