'''
Created on Dec 2, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [storage] section include the storage groups name
   -- <storage group name> array include the storage group names to be checked
   -- if you would like to check all the partitions, input <all>

e.g.
python checkStorageGroupsStatus.py t257.cfg all

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class checkStorageGroupsStatus:
    def __init__(self, sgNameList):
        
        self.dpmObj = dpm(cf)
        self.sgNameList = sgNameList
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)


    def run(self):
        
        print ("checkStorageGroupsStatus starting >>>")

        for cpcSg in self.dpmObj.cpc.list_associated_storage_groups():
            if cpcSg.get_property('type') == 'fcp':
                # only check for FCP storage groups
                sgName = cpcSg.get_property('name')
                sgStatus = cpcSg.get_property('fulfillment-state')
                if self.sgNameList == None or sgName in self.sgNameList:
                    self.logger.info(sgName + " in " + sgStatus + " state !")
        
        print ("checkStorageGroupsStatus completed ...")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        sgNameSection = sys.argv[2]
    else:
        print ("Please input the config file and storage group name array as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print ("Exit the program for config file read error")
        exit(1)
        
    if sgNameSection.lower() == 'all':
        sgNameList = None
    else:
        sgNameList = eval(configComm.sectionDict['storage'][sgNameSection])
    
    checkObj = checkStorageGroupsStatus(sgNameList)
    checkObj.run()