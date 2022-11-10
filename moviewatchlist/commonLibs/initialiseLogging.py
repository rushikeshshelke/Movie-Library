import logging

from logging.handlers import RotatingFileHandler
from moviewatchlist.commonLibs.globalVariables import GlobalVariables
from datetime import date
from moviewatchlist.commonLibs.commonConfigs import CommonConfigs

class InitialiseLogging:

    def setupLogging(self):
        logPath = GlobalVariables.APP_LOGS_PATH + "/" + str(date.today())
        CommonConfigs().createDir(logPath)
        appConfigPath = "{}/appConfigs.json".format(GlobalVariables.APP_CONFIG_PATh)
        jsonData = CommonConfigs().readJson(appConfigPath)
        logPath = "{}/{}".format(logPath,jsonData['filename'])
        handler = RotatingFileHandler(logPath,maxBytes=jsonData['maxSize'],backupCount=jsonData['rotateCount'])
        handler.setFormatter(logging.Formatter(jsonData['logFormat']))
        GlobalVariables.LOGGER = logging.getLogger(jsonData['appName'])
        GlobalVariables.LOGGER.setLevel(logging.DEBUG)
    
        if not GlobalVariables.LOGGER.hasHandlers():
            GlobalVariables.LOGGER.addHandler(handler)