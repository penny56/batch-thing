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

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class deletePartitions:
    def __init__(self, lcdpm, partNameList):

        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.partNameList = partNameList
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)
        

    def run(self):

        print "deletePartitions starting >>>"
        for partName in self.partNameList:
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                self.logger.info(partName + " delete failed -- could not find !!!")
                continue
            if str(partObj.get_property('status')) == 'stopped':
                try:
                    partObj.delete()
                    self.logger.info(partName + " delete successful")
                except (zhmcclient.HTTPError, Exception) as e:
                    self.logger.info(partName + " delete failed !!!")
                    os.system("echo 0 > ./enable")
                    # Record the failed log information
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info("<< " + partName + " partition delete failed by the following reason, reference WSAPI doc for code details explanation >>")
                    loggerFailed.info("===>")
                    loggerFailed.info("http_status: " + str(e.http_status))
                    loggerFailed.info("reason: " + str(e.reason))
                    loggerFailed.info("message: " + str(e.message))
                    loggerFailed.info("== The longevity script is stopped until you delete the enable file or echo it to 1 ==")
    
                    exit(1)
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
    
    deleteObj = deletePartitions(None, partNameList)
    deleteObj.run()