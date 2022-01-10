'''
Created on Mar 31, 2020

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [adapter] section include the adapter's name
   -- if you would like to check all the adapters, input <all>, and we only support <all> in current stage
   
e.g.
python checkAdaptersStatus.py t90.cfg all

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class checkAdaptersStatus:
    def __init__(self, adapterList):
        
        self.dpmObj = dpm(cf)
        self.adapterList = adapterList
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)


    def run(self):
        
        print ("checkAdaptersStatus starting >>>")
        
        for cpcAdapter in self.dpmObj.cpc.adapters.list(full_properties=True):
            adapterID = cpcAdapter.get_property('adapter-id')
            adapterType = cpcAdapter.get_property('type')
            adapterStatus = cpcAdapter.get_property('status')
            adapterState = cpcAdapter.get_property('state')
            adapterDesc = cpcAdapter.get_property('description')
            if self.adapterList == None:
                self.logger.info(adapterID + " | " + adapterType + " | " + adapterStatus + " | " + adapterState + " | " + adapterDesc)


                
        print ("checkAdaptersStatus completed ...")


if __name__ == '__main__':
    if len(sys.argv) == 3:
        cf = sys.argv[1]
        adapterSection = sys.argv[2]
    else:
        print ("Please input the config file and adapter array as a parameter!\nQuitting....")
        exit(1)
    
    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print ("Exit the program for config file read error")
        exit(1)

    if adapterSection.lower() == 'all':
        adapterList = None
    else:
        # only support the all parameter
        adapterList = None
    
    checkObj = checkAdaptersStatus(adapterList)
    checkObj.run()
