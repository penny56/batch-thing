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

import sys, time, os
from configFile import configFile
from dpm import dpm
from log import log
from stopPartitions import stopPartitions
from deletePartitions import deletePartitions
from createPartitions import createPartitions
from createvNics import createvNics
from attachStorageGroups import attachStorageGroups
from setBootOptions import setBootOptions
from startFcpStorageDiscovery import startFcpStorageDiscovery
from startPartitions import startPartitions


class partitionLifecycle:
    def __init__(self, partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict):
        
        self.dpmObj = dpm(cf)
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.vnicCommDict = vnicCommDict
        self.attachCommDict = attachCommDict
        self.bootCommDict = bootCommDict
        self.counter = 1
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)

    def run(self):

        print ("partitionLifecycle starting >>>")
        stopObj = stopPartitions(self.dpmObj, self.partNameList)
        delObj = deletePartitions(self.dpmObj, self.partNameList)
        createObj = createPartitions(self.dpmObj, self.partCommDict, self.partNameList)
        vNicObj = createvNics(self.dpmObj, self.vnicCommDict, self.partNameList)
        attachObj = attachStorageGroups(self.dpmObj, self.attachCommDict)
        bootObj = setBootOptions(self.dpmObj, self.bootCommDict)
        startFcpStorageDiscoveryObj = startFcpStorageDiscovery(self.dpmObj, self.bootCommDict)
        startObj = startPartitions(self.dpmObj, self.partNameList)

        for i in range(self.counter):
            stopObj.run()
            delObj.run()
            createObj.run()
            vNicObj.run()
            attachObj.run()
            bootObj.run()
            # skip this case temporarily
            # startFcpStorageDiscoveryObj.run()
            startObj.run()
            print ("partitionLifecycle sleeping -----------------------------------------------> 5s ...")
            time.sleep(5)
            
        print ("partitionLifecycle completed ...")


if __name__ == '__main__':

    if len(sys.argv) == 3:
        cf = sys.argv[1]
        partDict = sys.argv[2]
    else:
        print ("Please input the configure file name and key name in [lifecycle] as parameters!\nQuitting....")
        exit(1)

    # check if disabled file is enabled (get the cpc name from the config file path)
    disabled = "disabled" + '.' + cf.split('/')[-1].split('.')[0]
    if os.path.isfile(disabled):
        with open(disabled, 'r') as f:
            # get the 1st character in the 1st line
            if f.readlines()[0][0] == '1':
                print ("Exist with the disabled flag checked!")
                exit(0)

    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print ("Exit the program for configure file: " + cf + " load error!")
        exit(1)
        
    partDict = eval(configComm.sectionDict['lifecycle'][partDict])

    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partDict['partition']])
    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    attachCommDict = eval(configComm.sectionDict['attachment'][partDict['attachment']])
    bootCommDict = eval(configComm.sectionDict['bootoption'][partDict['bootoption']])
    
    lifecycleObj = partitionLifecycle(partCommDict, partNameList, vnicCommDict, attachCommDict, bootCommDict)    
    lifecycleObj.run()
