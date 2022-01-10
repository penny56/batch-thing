'''
Created on Nov 12, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the created vNic parameters
   -- <commondict> dictionary include the vNics common parameters
      like vNic name, device number, description and adapter information
   -- <partition name> array include the partitions' name which the vNics will be created in
      this option must be indicated in the command line as a parameter

e.g.
python createvNics.py rhel 

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class createvNics:
    def __init__(self, lcdpm, vnicCommDict, partNameList):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.vnicCommDict = vnicCommDict
        self.partNameList = partNameList
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)


    def run(self):

        print ("createvNics starting >>>")
        # Check if the adapter exist.
        try:
            adapter = self.dpmObj.cpc.adapters.find(name = self.vnicCommDict["adaptername"])
        except zhmcclient.NotFound as e:
            self.logger.info("vNic create failed for adapter: " + self.vnicCommDict["adaptername"] + " could not found !!!")
            return
        
        # Get the vSwitch
        vswitches = self.dpmObj.cpc.virtual_switches.findall(**{'backing-adapter-uri': adapter.uri})
        vswitch = None
        for vs in vswitches:
            if vs.get_property('port') == int(self.vnicCommDict["adapterport"]):
                vswitch = vs
                break
        
        # Construct the vNic template
        vnicTempl = dict()
        vnicTempl["description"] = self.vnicCommDict["desc"]
        vnicTempl["device-number"] = self.vnicCommDict["devnum"]
        vnicTempl["virtual-switch-uri"] = vswitch.uri
        
        for partName in self.partNameList:
            # get the partition
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                self.logger.info(partName + " delete failed -- could not find !!!")
                continue
            vnicTempl["name"] = partName + '_' + self.vnicCommDict["namesuffix"]
            
            # Create the vNic
            try:
                new_vnic = partObj.nics.create(vnicTempl)
                self.logger.info("vNic " + vnicTempl["name"] + " in partition " + partName + " created successful")
            except zhmcclient.HTTPError as e:
                self.logger.info("vNic " + vnicTempl["name"] + " in partition " + partName + " created failed !!!")
                os.system("echo 1 > ./disabled")
                # Record the failed log information
                loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                loggerFailed.info("<< vNic " + vnicTempl["name"] + " in partition " + partName + " created failed >>")
                loggerFailed.info("===>")
                loggerFailed.info("http_status: " + str(e.http_status))
                loggerFailed.info("reason: " + str(e.reason))
                loggerFailed.info("message: " + str(e.message))
                loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")

                exit(1)
            time.sleep(1)

        print ("createvNics completed ...")


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
        print ("Exit the program for config file read error")
        exit(1)

    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    partNameList = eval(configComm.sectionDict['partition'][partNameSection])

    vNicObj = createvNics(None, vnicCommDict, partNameList)
    vNicObj.run()
