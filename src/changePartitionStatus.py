'''
Created on Nov 23, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partition information
   -- <partition name> array include the partition name array which will be started or stopped
      this option must be indicated in the command line as a parameter 
   
e.g.
python changePartitionStatus.py t90.cfg ubuntu

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class changePartitionStatus:
    def __init__(self, partNameList):
        
        self.dpmObj = dpm(cf)
        self.partNameList = partNameList
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)
        # identify how many start/stop action will be executed totally
        self.counter = 6
        # identify the wait time until the start/stop action completed, 600 = 10mins
        self.timeout = 600


    def run(self):
        
        print "changePartitionStatus starting >>>"
        # Check partition status
        for i in range(self.counter):
            for partName in self.partNameList:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
                if str(partObj.get_property('status')) == 'active':
                    timespan = self.stopPartition(partObj)
                    if timespan:
                        self.logger.info(partName + " stop successful " + timespan)
                    else:
                        self.logger.info(partName + " stop failed !!!")
                elif str(partObj.get_property('status')) == 'stopped':
                    timespan = self.startPartition(partObj)
                    if timespan:
                        self.logger.info(partName + " start successful " + timespan)
                    else:
                        self.logger.info(partName + " start failed !!!")
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
        print "Exit the program for config file read error"
        exit(1)

    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    changeObj = changePartitionStatus(partNameList)
    changeObj.run()