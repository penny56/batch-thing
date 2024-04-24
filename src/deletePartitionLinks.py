'''
Created on Apr. 23, 2023

@author: mayijie
'''

import sys
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
                except Exception as exc:
                    print ("error")

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

