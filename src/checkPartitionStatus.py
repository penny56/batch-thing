'''
Created on Nov 18, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partitions name
   -- <partition name> array include the partition names to be checked
      this option must be indicated in the command line as a parameter
   -- if you would like to check all the partitions, input <all>
   
e.g.
python checkPartitionStatus.py t90.cfg all

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class checkPartitionStatus:
    def __init__(self, partNameList):
        
        self.dpmObj = dpm(cf)
        self.partNameList = partNameList
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)


    def run(self):
        
        print ("checkPartitionStatus starting >>>")
        
        for cpcPart in self.dpmObj.cpc.partitions.list():
            partName = cpcPart.get_property('name')
            status = cpcPart.get_property('status')
            if self.partNameList == None or partName in self.partNameList:
                self.logger.info(partName + " in " + status + " state !")

        '''
        for partName in self.partNameList:
            
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
                status = partObj.get_property('status')
                self.logger.info(partName + " in " + status + " state !")
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                self.logger.info(partName + "can't find !")
            time.sleep(1)
        '''
                
        print ("checkPartitionStatus completed ...")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        partNameSection = sys.argv[2]
    else:
        print ("Please input the config file and partition name array as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print ("Exit the program for config file read error")
        exit(1)

    if partNameSection.lower() == 'all':
        partNameList = None
    else:
        partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    checkObj = checkPartitionStatus(partNameList)
    checkObj.run()
