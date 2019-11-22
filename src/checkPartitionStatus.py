'''
Created on Nov 18, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partitions name
   -- <partition name> array include the partition names to be checked
      this option must be indicated in the command line as a parameter 
   
e.g.
python createPartitions.py longevity

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class checkPartitionStatus:
    def __init__(self, dpmConnDict, partNameList):
        
        self.dpmObj = dpm(dpmConnDict)
        self.partNameList = partNameList
        self.logger = log.getlogger(self.__class__.__name__)

    def start(self):
                
        for partName in self.partNameList:
            
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
                status = partObj.get_property('status')
                self.logger.info(partName + " in " + status + " state !")
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                self.logger.info(partName + "can't find !")
            time.sleep(1)
        
        print "checkPartitionStatus completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        partNameSection = sys.argv[1]
    else:
        print ("Please input the partition name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    partCreation = checkPartitionStatus(dpmConnDict, partNameList)
    partCreation.start()