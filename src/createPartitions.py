'''
Created on Nov 7, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the created partitions parameters
   -- <commondict> dictionary include the partition common parameters
      e.g. type and number of processor, memory
      and descriptions, every generated partition have the same parameters indicated in this dictionary
   -- <partition name> array include the partition names to be created
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

class createPartitions:
    def __init__(self, partCommDict, partNameList):
        
        self.dpmObj = dpm()
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.logger = log.getlogger(self.__class__.__name__)


    def run(self):
        
        print "createPartitions starting >>>"
        # construct partition template
        partitionTempl = dict()
        partitionTempl["type"] = self.partCommDict["par_type"]
        partitionTempl["description"] = self.partCommDict["par_desc"]
        partitionTempl["reserve-resources"] = True if (self.partCommDict["par_reserveresources"].lower() == 'true') else False
        partitionTempl["processor-mode"] = self.partCommDict["proc_mode"]
        partitionTempl["ifl-processors"] = int(self.partCommDict["proc_num"])
        if (int(self.partCommDict["init_mem"]) < 1024):
            partitionTempl["initial-memory"] = int(self.partCommDict["init_mem"]) * 1024
        else:
            partitionTempl["initial-memory"] = int(self.partCommDict["init_mem"])
        if (int(self.partCommDict["max_mem"]) < 1024):
            partitionTempl["maximum-memory"] = int(self.partCommDict["max_mem"]) * 1024
        else:
            partitionTempl["maximum-memory"] = int(self.partCommDict["max_mem"])
        
        for partName in self.partNameList:
            partitionTempl["name"] = partName
            
            try:
                new_partition = self.dpmObj.cpc.partitions.create(partitionTempl)
                self.logger.info(partName + " created successful")
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                self.logger.info(partName + " created failed !!!")
            time.sleep(1)
            
        print "createPartitions completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        partNameSection = sys.argv[1]
    else:
        print ("Please input the partition name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    partObj = createPartitions(partCommDict, partNameList)
    partObj.run()