import json
import os

class CommonConfigs:

    def createDir(self,path):
        if os.path.isdir(path) == False:
            os.makedirs(path)
    
    def readJson(self,filename):
        with open(filename,'r') as file:
            return json.load(file)