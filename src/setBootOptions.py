'''
Created on Nov 27, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the created vNic parameters
   -- <commondict> dictionary include the vNics common parameters
      like vNic name, device number, description and adapter information
   -- <partition name> array include the partitions' name which the vNics will be created in
      this option must be indicated in the command line as a parameter

Possible cases the set boot option fail:
-- Operation time out
-- Storage volume UUID typo
-- Storage volume UUID type not set to boot type
-- Storage group not attached to the partition or the state not in complete
-- Storage group not FCP

e.g.
python createvNics.py rhel 

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class setBootOptions:
    def __init__(self, bootCommDict):
        
        self.dpmObj = dpm()
        self.bootCommDict = bootCommDict
        self.logger = log.getlogger(self.__class__.__name__)


    def run(self):
        
        print "setBootOptions starting >>>"
        for partName, sg_sv in self.bootCommDict.items():
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            sgName = sg_sv.split(' ')[0]
            svUUID = sg_sv.split(' ')[-1]
            try:
                sgObj = self.dpmObj.cpc.list_associated_storage_groups(filter_args={'name' : sgName}).pop()
                svObj = sgObj.storage_volumes.list(filter_args={'uuid' : svUUID}).pop()
                bootTempl = dict()
                bootTempl['boot-storage-volume'] = svObj.uri
                partObj.update_properties(bootTempl)
                bootTempl2 = dict()
                bootTempl2['boot-device'] = 'storage-volume'
                partObj.update_properties(bootTempl2)
                self.logger.info("partition " + partName + " set boot option successful")
            except Exception as e:
                self.logger.info("partition " + partName + " set boot option sg: " + sgName + ", sv UUID: " + svUUID + ", failed !!!")
            
            time.sleep(1)

        print "setBootOptions completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 2:
        bootOptionDict = sys.argv[1]
        
    else:
        print ("Please input the boot option dictionary as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(None)
    configComm.loadConfig()
    bootCommDict = eval(configComm.sectionDict['bootoption'][bootOptionDict])

    bootObj = setBootOptions(bootCommDict)
    bootObj.run()