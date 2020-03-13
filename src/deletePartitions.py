'''
Created on Nov 26, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partition information
   -- <partition name> array include the partition name array which will be started or stopped
      this option must be indicated in the command line as a parameter 
   
e.g.
python deletePartitions.py t90.cfg ubuntu

@author: mayijie
'''

import sys
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class deletePartitions:
    def __init__(self, partNameList):
        
        self.dpmObj = dpm(cf)
        self.partNameList = partNameList
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)


    def run(self):

        print "deletePartitions starting >>>"
        for partName in self.partNameList:
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                continue
            if str(partObj.get_property('status')) == 'stopped':
                try:
                    partObj.delete()
                    self.logger.info(partName + " delete successful ")
                except (zhmcclient.HTTPError, Exception) as e:
                    self.logger.info(partName + " delete failed !!!")
            else:
                self.logger.info(partName + " delete failed for in " + str(partObj.get_property('status')) + " state !!!")
        
        print "deletePartitions completed ..."


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        partNameSection = sys.argv[2]
    else:
        print ("Please input the config file and vNic creation model as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print "Exit the program for config file read error"
        exit(1)

    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    deleteObj = deletePartitions(partNameList)
    deleteObj.run()