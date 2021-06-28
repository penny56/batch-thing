'''
Created on Nov 13, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [attachment] section include the attachment parameters
   -- <partition dictionary> dictionary include the partitions, storage groups and the device number information
      the partition name as the keys of the dictionary, the values are also a dictionary,
      in the sub-dictionary, the keys are the storage groups' name, and the values are the device number array.
      this option must be indicated in the command line as a parameter
   
e.g.
python attachStorageGroups.py t90.cfg suse

@author: mayijie
'''

import sys, time, os
import zhmcclient
from configFile import configFile
from dpm import dpm
from log import log

class attachStorageGroups:
    def __init__(self, lcdpm, attachCommDict):
        
        if lcdpm == None:
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.attachCommDict = attachCommDict
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)

    def run(self):

        print "attachStorageGroups starting >>>"
        for partName,  sgDict in self.attachCommDict.items():
            try:
                partObj = self.dpmObj.cpc.partitions.find(name = partName)
            except Exception as e:
                self.logger.info(partName + " attach storage groups failed -- could not find !!!")
                continue
            
            for sgName, devnumArray in sgDict.items():
                ret = self.getStorageGroupEntity (sgName)
                if ret['success']:
                    sgObj = ret['object']
                else:
                    self.logger.info("Partition " + partName + " attach storage group " + sgName + " " + ret['object'] + " failed !!!")
                    continue

                # attach the storage group to the partition
                try:
                    partObj.attach_storage_group(sgObj)
                    self.logger.info("Partition " + partName + " attach storage group " + sgName + " successful")
                except Exception as e:
                    self.logger.info("Partition " + partName + " attach storage group " + sgName + " exception failed !!!")
                    os.system("echo 0 > ./enable")
                    # Record the failed log information
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info("<< Partition " + partName + " attach storage group " + sgName + " exception failed >>")
                    loggerFailed.info("===>")
                    loggerFailed.info("http_status: " + str(e.http_status))
                    loggerFailed.info("reason: " + str(e.reason))
                    loggerFailed.info("message: " + str(e.message))
                    loggerFailed.info("== The longevity script is stopped until you delete the enable file or echo it to 1 ==")
    
                    exit(1)
                
                # update the device numbers

                # devnumArray[:] is a slice of devnumArray but with a new object
                # we use this to avoid the pop operation impact the original
                self.updateDeviceNumbers(str(partObj.uri), sgObj, devnumArray[:])
            
            time.sleep(1)

        print "attachStorageGroups completed ..."

    '''
    Verify and return the Storage Group entity by storage group name
    
    return:
        {'success': True/False,
         'object': <sgObj>/[None]
         }
    '''
    def getStorageGroupEntity (self, sgName):

        result = dict()
        
        try:
            for cpcSg in self.dpmObj.cpc.list_associated_storage_groups():
                if cpcSg.get_property('name') == sgName:
                    if cpcSg.get_property('fulfillment-state') == 'complete':
                        result['success'] = True
                        result['object'] = cpcSg
                    else:
                        result['success'] = False
                        result['object'] = "not in complete state"
            if not result:
                result['success'] = False
                result['object'] = "could not found"
        except zhmcclient.HTTPError as e:
            result['success'] = False
            result['object'] = "Exception occurred"
        
        return result
        
    def updateDeviceNumbers(self, partUri, sgObj, devnumArray):

        try:
            vsrs = sgObj.virtual_storage_resources.list()
        except zhmcclient.HTTPError:
            return None
        
        # eliminate the vsrs not belong to this partition
        vsrsii = []
        for vsr in vsrs:
            if str(vsr.get_property('partition-uri')) == partUri:
                vsrsii.append(vsr)
        
        if len(devnumArray) == len(vsrsii):
            for vsr in vsrsii:
                newValue = dict()
                adapterDesc = self.getAdapterDesc(vsr.get_property('adapter-port-uri'))

                if "Cisco" in adapterDesc.split(' '):
                    # for cisco, they use the smaller device number, make the smallest to the last
                    devnumArray.sort(reverse=True)
                elif "Brocade" in adapterDesc.split(' '):
                    # for brocade vhba, they use the bigger device number, put the biggest to the last
                    devnumArray.sort()

                newValue['device-number'] = str(devnumArray.pop())
                try:
                    vsr.update_properties(newValue)
                except zhmcclient.HTTPError as e:
                    self.logger.info("exception failed when setting device numbers " + str(newValue) + " !!!")
                    os.system("echo 0 > ./enable")
                    # Record the failed log information
                    loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                    loggerFailed.info("<< Exception failed when setting device numbers " + str(newValue) + " >>")
                    loggerFailed.info("===>")
                    loggerFailed.info("http_status: " + str(e.http_status))
                    loggerFailed.info("reason: " + str(e.reason))
                    loggerFailed.info("message: " + str(e.message))
                    loggerFailed.info("== The longevity script is stopped until you delete the enable file or echo it to 1 ==")
    
                    exit(1)
                    
        else:
            print "Number of devnum array element: %d not equals to number of vsrs in this partition: %d." %(len(devnumArray), len(vsrsii))
            return None

    def getAdapterDesc(self, adapterPortUri):

        adapterUri = adapterPortUri.split('/storage-ports/')[0]
        filter_args = {'object-uri': adapterUri}
        adapterObjs = self.dpmObj.cpc.adapters.list(full_properties=True, filter_args=filter_args)
        return adapterObjs[0].get_property("description")


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

    attachCommDict = eval(configComm.sectionDict['attachment'][partNameSection])
    
    attachObj = attachStorageGroups(None, attachCommDict)
    attachObj.run()