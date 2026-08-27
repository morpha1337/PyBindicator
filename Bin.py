from time import struct_time, mktime, time, localtime
from Helpers import struct_TimeToString, stringToStruct_Time, getTodayAsEpoch, getDaysToSeconds
import json

class Bin:
    Label: str
    NextCollectionDate: struct_time
    Color: tuple
    CollectionFrequency: int  # in seconds

    def __init__(self, _label: str, _nextCollectionDate: struct_time, _color: tuple, _collectionFrequency: int):
        self.Label = _label
        self.NextCollectionDate = _nextCollectionDate
        self.Color = _color
        self.CollectionFrequency = _collectionFrequency

    def __str__(self):
        return "Label: %s, NextCollectionDate: %s, Color: %s" % (self.Label, self.NextCollectionDate, self.Color)

    def toJson(self) -> json:
        return {"Label": self.Label,
                "Color": self.Color,
                "NextCollectionDate": struct_TimeToString(self.NextCollectionDate),
                "CollectionFrequency": self.CollectionFrequency}

    def hasExpired(self, endTime: int = 0) -> bool:
        expiryTime = mktime(self.NextCollectionDate) + endTime
        return (expiryTime < time())

    def isActive(self, startTime: int = 0, endTime: int = 0) -> bool:
        nextCollectionDateInSeconds = mktime(self.NextCollectionDate)
        alertStartTime = nextCollectionDateInSeconds - startTime
        alertEndTime = nextCollectionDateInSeconds + endTime
        now = time()
        return (now > alertStartTime and now < alertEndTime )

    def setNextCollectionDate(self) -> None:
        today = getTodayAsEpoch()
        while (self.NextCollectionDate < today):
            self.NextCollectionDate += self.CollectionFrequency

def convertJsonToBin(binData: json) -> [Bin]:
    # need to figure out how to save a tuple as JSON.
    # for each raw Bin. Calculate the next bin date.
    # then return the array of bins to the program.
    bins = []
    for rawBin in binData:
        startDate = stringToStruct_Time(rawBin["startDate"])
        startDateInSecondsSinceEpoch = mktime(startDate)
        freqencyInSeconds = getDaysToSeconds(int(rawBin["frequencyInDays"]))
        todayInSecondsSinceEpoch = getTodayAsEpoch()
        nextCollectionDate = startDateInSecondsSinceEpoch

        # get Next Collection Date
        while nextCollectionDate < todayInSecondsSinceEpoch:
            nextCollectionDate += freqencyInSeconds

        nextCollectionDateAsStruct = localtime(nextCollectionDate)
        newBin = Bin(rawBin["label"], nextCollectionDateAsStruct, rawBin["color"], freqencyInSeconds)
        bins.append(newBin)

    return bins
