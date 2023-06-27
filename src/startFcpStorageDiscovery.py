'''
Created on Jun 27, 2023

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class startFcpStorageDiscovery:
    def __init__(self, lcdpm, bootCommDict):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.bootCommDict = bootCommDict
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)
        self.timeout = 60*5


    def run(self):

        print ("startFcpStorageDiscovery starting >>>")
        for sg_sv in self.bootCommDict.values():
            sgName = sg_sv.split(' ')[0]

            try:
                sgObj = self.dpmObj.cpc.list_associated_storage_groups(filter_args={'name' : sgName}).pop()

                tBegin = int(time.time())
                sgObj.discover_fcp(force_restart=False, wait_for_completion=True, operation_timeout=self.timeout)
                tEnd = int(time.time())

                self.logger.info(sgName + " storage group LUN discovery takes " + str(tEnd - tBegin) + " seconds")

            except (zhmcclient.Error, Exception) as e:
                self.logger.info("Storage group " + sgName + " start Fcp Storage Discovery failed !!!")
                os.system("echo 1 > ./%s" % ("disabled" + "." + self.dpmObj.cpc_name.lower()))
                # Generate a log file dedicate for this failure.
                loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                loggerFailed.info("Storage group " + sgName + " start Fcp Storage Discovery failed !!!")
                loggerFailed.info("<Exception sub-class>: [http_status],[reason]: <message> FORMAT >>")
                loggerFailed.info("{}: {}".format(e.__class__.__name__, e))
                loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")

                exit(1)

        print ("startFcpStorageDiscovery completed ...")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        bootOptionDict = sys.argv[2]
    else:
        print ("Please input the config file and boot option dictionary as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print ("Exit the program for config file read error")
        exit(1)

    bootCommDict = eval(configComm.sectionDict['bootoption'][bootOptionDict])

    bootObj = startFcpStorageDiscovery(None, bootCommDict)
    bootObj.run()
