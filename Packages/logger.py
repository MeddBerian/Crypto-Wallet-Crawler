import logging
import os


class Logger:
    def __init__(self, logFileName):
        logFormatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        self.rootLogger = logging.getLogger(__name__)
        self.rootLogger.setLevel(logging.DEBUG)

        if not os.path.isdir('Logs'):
            os.mkdir("Logs")

        fileHandler = logging.FileHandler(f"Logs/{logFileName}.log")
        fileHandler.setFormatter(logFormatter)
        self.rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.rootLogger.addHandler(consoleHandler)

    
    def debug(self, message):
        self.rootLogger.debug(message)
        
    
    def info(self, message):
        self.rootLogger.info(message)

    def warning(self, message):
        self.rootLogger.warning(message)

    def error(self, message):
        self.rootLogger.error(message)

    def critical(self, message):
        self.rootLogger.critical(message)



