'''
Created on Dec 2, 2019

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

class checkStorageGroupsStatus:
    def __init__(self, sgNameList):
        
        self.dpmObj = dpm()
        self.sgNameList = sgNameList
        self.logger = log.getlogger(self.__class__.__name__)


    def run(self):
        
        print "checkStorageGroupsStatus starting >>>"

        for cpcSg in self.dpmObj.cpc.list_associated_storage_groups():
            if cpcSg.get_property('type') == 'fcp':
                # only check for FCP storage groups
                sgName = cpcSg.get_property('name')
                sgStatus = cpcSg.get_property('fulfillment-state')
                if self.sgNameList == None or sgName in self.sgNameList:
                    self.logger.info(sgName + " in " + sgStatus + " state !")
        
        print "checkStorageGroupsStatus completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sgNameSection = sys.argv[1]
    else:
        print ("Please input the storage group name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    if sgNameSection.lower() == 'all':
        sgNameList = None
    else:
        sgNameList = eval(configComm.sectionDict['storage'][sgNameSection])
    
    checkObj = checkStorageGroupsStatus(sgNameList)
    checkObj.run()