'''
Created on Nov 27, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [partition] section include the created vNic parameters
   -- <commondict> dictionary include the vNics common parameters
      like vNic name, device number, description and adapter information
   -- <partition name> array include the partitions' name which the vNics will be created in
      this option must be indicated in the command line as a parameter

Possible cases the set boot option fail:
-- Operation time out
-- Storage volume UUID typo
-- Storage volume UUID type not set to boot type
-- Storage group not attached to the partition or the state not in complete
-- Storage group not FCP

e.g.
python setBootOptions.py t90.cfg rhel 

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class setBootOptions:
    def __init__(self, lcdpm, bootCommDict):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.bootCommDict = bootCommDict
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)
        self.timeout = 600


    def run(self):
        
        print ("setBootOptions starting >>>")
        for partName, sg_sv in self.bootCommDict.items():
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            sgName = sg_sv.split(' ')[0]
            svUUID = sg_sv.split(' ')[-1]
            stage = "Stage: "
            try:
                sgObj = self.dpmObj.cpc.list_associated_storage_groups(filter_args={'name' : sgName}).pop()
                svObj = sgObj.storage_volumes.list(filter_args={'uuid' : svUUID}).pop()
                bootTempl = dict()
                bootTempl['boot-storage-volume'] = svObj.uri
                partObj.update_properties(bootTempl)
                stage += "1/3) set 'boot-storage-volume = volume uri' "
                bootTempl.clear()
                bootTempl['boot-device'] = 'storage-volume'
                partObj.update_properties(bootTempl)
                stage += "2/3) set 'boot-device = storage-volume' "
                bootTempl.clear()
                bootTempl['boot-timeout'] = self.timeout
                partObj.update_properties(bootTempl)
                stage += "3/3) set 'boot-timeout = 600' "
                self.logger.info("partition " + partName + " set boot option successful")
            except (zhmcclient.Error, Exception) as e:
                self.logger.info("partition " + partName + " set boot option sg: " + sgName + ", sv UUID: " + svUUID + ", failed !!!")
                os.system("echo 1 > ./%s" % ("disabled" + "." + self.dpmObj.cpc_name.lower()))
                # Generate a log file dedicate for this failure.
                loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                loggerFailed.info(partName + " partition set boot option failed. >>")
                loggerFailed.info("<Exception sub-class>: [http_status],[reason]: <message> FORMAT >>")
                loggerFailed.info("{}: {}".format(e.__class__.__name__, e))
                loggerFailed.info(stage)
                loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")

                exit(1)

            time.sleep(1)

        print ("setBootOptions completed ...")


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

    bootObj = setBootOptions(None, bootCommDict)
    bootObj.run()
