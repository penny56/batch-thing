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

    def run(self):

        print ("stopPartitions starting >>>")
        for partName in self.partNameList:
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                self.logger.info(partName + " stop failed -- could not find !!!")
                continue
            # ??? exception: HTTPError: 404,1: Not found or not authorized [GET /api/partitions/d64092b6-1116-11ea-b8df-00106f24553e]
            if str(partObj.get_property('status')) == 'active':
                try:
                    tBegin = int(time.time())
                    partObj.stop(wait_for_completion = True, operation_timeout = self.timeout)
                    tEnd = int(time.time())
                    self.logger.info(partName + " partition stopped successful in " + str(tEnd - tBegin) + " seconds")
                except zhmcclient.Error as e:
                    self.logger.info(partName + " stop failed !!!")
                    os.system("echo 1 > ./%s" % ("disabled" + "." + self.dpmObj.cpc_name.lower()))
                    # Generate a log file dedicate for this failure.
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info(partName + " partition stop failed by the following reason >>")
                    loggerFailed.info("<Exception sub-class>: [http_status],[reason]: <message> FORMAT >>")
                    loggerFailed.info("{}: {}".format(e.__class__.__name__, e))
                    loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")
    
                    exit(1)
            else:
                self.logger.info(partName + " stop skipped for in " + str(partObj.get_property('status')) + " state !!!")

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
