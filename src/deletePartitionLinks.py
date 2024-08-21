'''
Created on Apr. 23, 2023

@author: mayijie
'''

import sys, os, time
from configFile import configFile
from dpm import dpm
from log import log
from prsm2api import prsm2api
from urllib.parse import urlencode

class deletePartitionLinks:
    def __init__(self, lcdpm):
        
        if lcdpm == None:
            # for launch from this case only
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)

    def run(self):

        print ("deletePartitionLinks starting >>>")
        plTypeSet = {'smc-d', 'hipersockets', 'ctc'}

        for plType in plTypeSet:
            
            plName = self.dpmObj.cpc_name + '-' + plType + '-' + "longevity"
            # if the partition link already exist in the CPC
            try:
                query = urlencode({'name': plName})
                res = prsm2api.listPartitionLinks(self.dpmObj.hmc, query)
            except Exception as exc:
                print ("partition link: " + plName + " Not exist!")

            if len(res) != 0:        
                plID = res[0]['object-uri'].replace('/api/partition-links/','')
                try:
                    prsm2api.deletePartitionLinks(self.dpmObj.hmc, plID, {})
                    self.logger.info(plName + " delete successful")
                except Exception as e:
                    self.logger.info(plName + " delete failed !!!")
                    os.system("echo 1 > ./%s" % ("disabled" + "." + self.dpmObj.cpc_name.lower()))
                    # Generate a log file dedicate for this failure.
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info(plName + " partition link delete failed. >>")
                    loggerFailed.info("<Exception sub-class>: [http_status],[reason]: <message> FORMAT >>")
                    loggerFailed.info("{}: {}".format(e.__class__.__name__, e))
                    loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")

                    exit(1)
            time.sleep(5)

        print ("deletePartitionLinks completed ...")

if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        partNameSection = sys.argv[2]
    else:
        print ("Please input the config file and partition name array as a parameter!\nQuitting....")
        exit(1)

    partObj = deletePartitionLinks(None)
    partObj.run()

