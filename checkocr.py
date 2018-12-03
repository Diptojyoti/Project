#helps print the statements in a json format
# import the necessary packages
import json


class CheckOCR:
    def __init__(self, imageName, amtword, amtnum, micr):
        self.imageName= imageName
        self.amtword=amtword
        self.amtnum=amtnum
        self.micr=micr

    def returnjson(self):
        return self
class MICR:
    def __init__(self, actnum, routnum, checknum):
        self.actnum=actnum
        self.routnum=routnum
        self.checknum=checknum
        