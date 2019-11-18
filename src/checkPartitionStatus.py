'''
Created on Nov 18, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partitionStatus] section include the partitions name
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
from cgi import logfile

class checkPartitionStatus:
    def __init__(self, dpmConnDict, partNameList, lf):
        
        self.dpmObj = dpm(dpmConnDict)
        self.partNameList = partNameList
        self.lf = lf

    def start(self):
        
        logFile = open(self.lf, 'w+')
        
        for partName in self.partNameList:
            
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
                status = partObj.get_property('status')
                line = partName + " in " + status + " state !"
                print line
                logFile.write(line + '\n')
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                line = partName + "can't find !"
                print line
                logFile.write(line + '\n')
            time.sleep(1)
        
        logFile.close()
        
        print "checkPartitionStatus completed ..."

cf = 'config.cfg'
lf = 'partStatus' + time.strftime('%Y%m%d') +'.log'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        partNameSection = sys.argv[1]
    else:
        print ("Please input the partition name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(cf)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    partNameList = eval(configComm.sectionDict['partitionStatus'][partNameSection])
    
    partCreation = checkPartitionStatus(dpmConnDict, partNameList, lf)
    partCreation.start()