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
    def __init__(self, partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict):
        
        self.dpmObj = dpm()
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.vnicCommDict = vnicCommDict
        self.attachCommDict = attachCommDict
        self.bootCommDict = bootCommDict
        self.counter = 2
        self.logger = log.getlogger(self.__class__.__name__)

    def run(self):

        print "partitionLifecycle starting >>>"
        stopObj = stopPartitions(self.partNameList)
        delObj = deletePartitions(self.partNameList)
        createObj = createPartitions(self.partCommDict, self.partNameList)
        vNicObj = createvNics(self.vnicCommDict, self.partNameList)
        attachObj = attachStorageGroups(self.attachCommDict)
        bootObj = setBootOptions(self.bootCommDict)
        startObj = startPartitions(self.partNameList)

        for i in range(self.counter):
            stopObj.run()
            for partName, timespan in stopObj.timespan.items():
                self.logger.info(partName + " stop successful " + timespan)
            # ??? Sometimes delete partition failed due to in stopping state
            time.sleep(30)
            delObj.run()
            createObj.run()
            vNicObj.run()
            attachObj.run()
            bootObj.run()
            startObj.run()
            for partName, timespan in startObj.timespan.items():
                self.logger.info(partName + " start successful " + timespan)
            
            print "partitionLifecycle sleeping -----------------------------------------------> 30s ..."
            time.sleep(30)
            
        print "partitionLifecycle completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        partDict = sys.argv[1]
    else:
        print ("Please input the partition dictionary as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    partDict = eval(configComm.sectionDict['lifecycle'][partDict])

    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partDict['partition']])
    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    attachCommDict = eval(configComm.sectionDict['attachment'][partDict['attachment']])
    bootCommDict = eval(configComm.sectionDict['bootoption'][partDict['bootoption']])
    
    lifecycleObj = partitionLifecycle(partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict)    
    lifecycleObj.run()