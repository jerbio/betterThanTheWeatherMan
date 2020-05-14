import datetime

def dayIndexFromStart(time):
    '''
        Giving a time after 1970 Jan 1 this function returns the number of days from 1970 Jan 1 12:00 AM rounded down
    '''
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')

    retValue = int((time - beginningOfTime).days)
    return retValue


def timeFromDayIndex(dayIndex):
    beginningOfTime_str = "1970-01-01 00:00:00"
    beginningOfTime = datetime.datetime.strptime(beginningOfTime_str, '%Y-%m-%d %H:%M:%S')
    retValue = beginningOfTime + datetime.timedelta(days=(dayIndex))

    return retValue
