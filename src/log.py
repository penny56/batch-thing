'''
Created on Nov 22, 2019

log class is for record the run log, it has two objects:

-- fileLog is for write the log into .log file, the name of .log file is input parameter 'name'
-- consoleLog is for show the log into console real-time.

@author: mayijie
'''

import logging

class log:
    
    @classmethod
    def getlogger(cls, name):
        
        logger = logging.getLogger(name)
        logger.setLevel(level = logging.INFO)
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        
        fileLog = logging.FileHandler(name + '.log')
        fileLog.setFormatter(formatter)
        
        consoleLog = logging.StreamHandler()
        consoleLog.setFormatter(formatter)
        
        logger.addHandler(fileLog)
        logger.addHandler(consoleLog)
        
        return logger
