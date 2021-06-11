'''
Created on Nov 22, 2019

-- Logger: interface for the program using the logging model.
-- Handler: where to output the log, console or file?
-- Filter: output filter, what level to output
-- Formatter: record content and format

@author: mayijie
'''

import logging

class log:
    
    @classmethod
    def getlogger(cls, name):
        
        logger = logging.getLogger(name)
        logger.setLevel(level = logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(message)s')
        
        # consoleLog object is for show the log into console real-time
        consoleLog = logging.StreamHandler()
        consoleLog.setFormatter(formatter)
        
        # fileLog object is for write the log into .log file, the name of .log file is input parameter 'name'
        fileLog = logging.FileHandler(name + '.log')
        fileLog.setFormatter(formatter)
        
        logger.addHandler(fileLog)
        logger.addHandler(consoleLog)
        
        return logger
