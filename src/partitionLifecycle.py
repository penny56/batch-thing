'''
Created on Nov 26, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partition information
   -- <partition name> array include the partition name array which will be started or stopped
      this option must be indicated in the command line as a parameter 
   
e.g.
python createPartitions.py ubuntu

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log
from stopPartitions import stopPartitions
from deletePartitions import deletePartitions
from createPartitions import createPartitions
from createvNics import createvNics
from attachStorageGroups import attachStorageGroups
from setBootOptions import setBootOptions
from startPartitions import startPartitions

class partitionLifecycle:
    def __init__(self, dpmConnDict, partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict):
        
        self.dpmObj = dpm(dpmConnDict)
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.vnicCommDict = vnicCommDict
        self.attachCommDict = attachCommDict
        self.bootCommDict = bootCommDict
        self.counter = 3
        self.logger = log.getlogger(self.__class__.__name__)

    def start(self, dpmConnDict):
        
        for i in range(self.counter):
            stopObj = stopPartitions(dpmConnDict, self.partNameList)
            stopObj.start()
            delObj = deletePartitions(dpmConnDict, self.partNameList)
            delObj.start()
            createObj = createPartitions(dpmConnDict, self.partCommDict, self.partNameList)
            createObj.start()
            vNicObj = createvNics(dpmConnDict, self.vnicCommDict, self.partNameList)
            vNicObj.start()
            attachObj = attachStorageGroups(dpmConnDict, self.attachCommDict)
            attachObj.start()
            bootObj = setBootOptions(dpmConnDict, self.bootCommDict)
            bootObj.start()
            startObj = startPartitions(dpmConnDict, self.partNameList)
            startObj.start()
            for partName, timespan in startObj.timespan.items():
                self.logger.info(partName + " start timespan " + timespan)
            
            time.sleep(60)
        
        print "partitionLifecycle completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        partDict = sys.argv[1]
    else:
        print ("Please input the partition dictionary as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    partDict = eval(configComm.sectionDict['lifecycle'][partDict])

    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partDict['partition']])
    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    attachCommDict = eval(configComm.sectionDict['attachment'][partDict['attachment']])
    bootCommDict = eval(configComm.sectionDict['bootoption'][partDict['bootoption']])
    
    lifecycleObj = partitionLifecycle(dpmConnDict, partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict)    
    lifecycleObj.start(dpmConnDict)