'''
Created on Nov 7, 2019

There will have two config files:
-- partitionComm.cfg: this file will indicate the common parameters like number of processors, memories etc.
-- partitionName.cfg: this file will indicate the partition name, it have several sections
                      each section have a group of names.

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm

class createPartitions:
    def __init__(self, dpmConnDict, partCommDict, partNameList):
        
        self.dpmObj = dpm(dpmConnDict)
        self.partCommDict = partCommDict
        self.partNameList = partNameList

    def start(self):
        
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
        
        for partName in partNameList:
            partitionTempl["name"] = partName
            
            try:
                new_partition = self.dpmObj.cpc.partitions.create(partitionTempl)
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                pass
            time.sleep(1)
            
            try:
                parRet = self.dpmObj.cpc.partitions.find(name = partitionTempl["name"])
                self.dpmObj.partition = parRet
            except zhmcclient.NotFound as e:
                pass
            time.sleep(1)
            
        print "createPartitions completed ..."

partCommCfg = 'partitionComm.cfg'
partNameCfg = 'partitionName.cfg'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        partNameSecName = sys.argv[1]
    else:
        print ("Please input the partition name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(partCommCfg)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    partCommDict = configComm.sectionDict['partCommon']
    
    configName = configFile(partNameCfg)
    configName.loadConfig()
    partNameList = eval(configName.sectionDict['partGroup'][partNameSecName])
    
    partCreation = createPartitions(dpmConnDict, partCommDict, partNameList)
    partCreation.start()