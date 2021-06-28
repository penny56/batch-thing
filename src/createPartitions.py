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
python createPartitions.py t90.cfg ubuntu

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class createPartitions:
    def __init__(self, lcdpm, partCommDict, partNameList):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.partCommDict = partCommDict
        self.partNameList = partNameList
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)


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
            
        partitionTempl['boot-timeout'] = 60
        
        for partName in self.partNameList:
            partitionTempl["name"] = partName
            
            try:
                new_partition = self.dpmObj.cpc.partitions.create(partitionTempl)
                self.logger.info(partName + " created successful")
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                self.logger.info(partName + " created failed !!!")
                os.system("echo 0 > ./enable")
                # Record the failed log information
                loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                loggerFailed.info("<< " + partName + " partition create failed by the following reason, reference WSAPI doc for code details explanation >>")
                loggerFailed.info("===>")
                loggerFailed.info("http_status: " + str(e.http_status))
                loggerFailed.info("reason: " + str(e.reason))
                loggerFailed.info("message: " + str(e.message))
                loggerFailed.info("== The longevity script is stopped until you delete the enable file or echo it to 1 ==")

                exit(1)
            time.sleep(1)
            
        print "createPartitions completed ..."


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

    partCommDict = eval(configComm.sectionDict['partition']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    partObj = createPartitions(None, partCommDict, partNameList)
    partObj.run()