'''
Created on Nov 26, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the partition information
   -- <partition name> array include the partition name array which will be started or stopped
      this option must be indicated in the command line as a parameter 
   
e.g.
python stopPartitions.py t90.cfg ubuntu

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class stopPartitions:
    def __init__(self, lcdpm, partNameList):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.partNameList = partNameList
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)
        # identify the wait time until the start/stop action completed, 600 = 10mins
        self.timeout = 600
        # To out put to lifecycle module
        self.timespan = dict()


    def run(self):

        print ("stopPartitions starting >>>")
        for partName in self.partNameList:
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                self.logger.info(partName + " stop failed -- could not find !!!")
                continue
            # ??? exception: HTTPError: 404,1: Not found or not authorized [GET /api/partitions/d64092b6-1116-11ea-b8df-00106f24553e]
            if str(partObj.get_property('status')) != 'stopped':
                start = int(time.time())
                try:
                    partObj.stop(wait_for_completion = True, operation_timeout = self.timeout)
                except (zhmcclient.HTTPError, Exception) as e:
                    self.logger.info(partName + " stop failed !!!")
                    os.system("echo 1 > ./disabled")
                    # Record the failed log information
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info("<< " + partName + " partition stop failed by the following reason, reference WSAPI doc for code details explanation >>")
                    loggerFailed.info("===>")
                    loggerFailed.info("http_status: " + str(e.http_status))
                    loggerFailed.info("reason: " + str(e.reason))
                    loggerFailed.info("message: " + str(e.message))
                    loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")
    
                    exit(1)
                end = int(time.time())
                self.logger.info(partName + " stop successful " + str(end - start))
                self.timespan[partName] = str(end - start)
            else:
                self.logger.info(partName + " stop failed for in " + str(partObj.get_property('status')) + " state !!!")

        print ("stopPartitions completed ...")


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
        
    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    stopObj = stopPartitions(None, partNameList)
    stopObj.run()
