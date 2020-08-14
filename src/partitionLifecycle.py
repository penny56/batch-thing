'''
Created on Nov 26, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partition information
   -- <partition name> array include the partition name array which will be started or stopped
      this option must be indicated in the command line as a parameter 
   
e.g.
python partitionLifecycle.py t90.cfg ubuntu

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
        
        self.dpmObj = dpm(cf)
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.vnicCommDict = vnicCommDict
        self.attachCommDict = attachCommDict
        self.bootCommDict = bootCommDict
        self.counter = 2
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)

    def run(self):

        print "partitionLifecycle starting >>>"
        stopObj = stopPartitions(self.dpmObj, self.partNameList)
        delObj = deletePartitions(self.dpmObj, self.partNameList)
        createObj = createPartitions(self.dpmObj, self.partCommDict, self.partNameList)
        vNicObj = createvNics(self.dpmObj, self.vnicCommDict, self.partNameList)
        attachObj = attachStorageGroups(self.dpmObj, self.attachCommDict)
        bootObj = setBootOptions(self.dpmObj, self.bootCommDict)
        startObj = startPartitions(self.dpmObj, self.partNameList)

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
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        partDict = sys.argv[2]
    else:
        print ("Please input the config file and partition dictionary as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print "Exit the program for config file read error"
        exit(1)
        
    partDict = eval(configComm.sectionDict['lifecycle'][partDict])

    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partDict['partition']])
    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    attachCommDict = eval(configComm.sectionDict['attachment'][partDict['attachment']])
    bootCommDict = eval(configComm.sectionDict['bootoption'][partDict['bootoption']])
    
    lifecycleObj = partitionLifecycle(partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict)    
    lifecycleObj.run()