'''
Created on Nov 23, 2019

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

class changePartitionStatus:
    def __init__(self, dpmConnDict, partNameList):
        
        self.dpmObj = dpm(dpmConnDict)
        self.partNameList = partNameList
        self.logger = log.getlogger(self.__class__.__name__)
        self.timeout = 600

    def start(self):
        
        # Check partition status
        for partName in self.partNameList:
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            if str(partObj.get_property('status')) == 'active':
                timespan = self.stopPartition(partObj)
                if timespan:
                    self.logger.info("stop succeed " + timespan)
                else:
                    self.logger.info("stop failed !!!")
            elif str(partObj.get_property('status')) == 'stopped':
                timespan = self.startPartition(partObj)
                if timespan:
                    self.logger.info("start succeed " + timespan)
                else:
                    self.logger.info("start failed !!!")
            else:
                # wait for the next loop
                pass

        print "changePartitionStatus completed ..."

    def startPartition(self, partObj):
        
        start = int(time.time())
        try:
            partObj.start(wait_for_completion = True, operation_timeout = self.timeout, status_timeout = self.timeout)
        except (zhmcclient.HTTPError, Exception) as e:
            return None
        end = int(time.time())
        
        return str(end - start)

    def stopPartition(self, partObj):
        
        start = int(time.time())
        try:
            partObj.stop(wait_for_completion = True, operation_timeout = self.timeout)
        except (zhmcclient.HTTPError, Exception) as e:
            return None
        end = int(time.time())
        
        return str(end - start)
        
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
    
    changeObj = changePartitionStatus(dpmConnDict, partNameList)
    changeObj.start()