'''
Created on Nov 13, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [attachment] section include the attachment parameters
   -- <commondict> dictionary include the partitions, storage groups and the device number information
      the partition name as the keys of the dictionary, the values are also a dictionary,
      in the sub-dictionary, the keys are the storage groups' name, and the values are the device number array.
   
e.g.
python attachStorageGroups.py

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm

class attachStorageGroups:
    def __init__(self, dpmConnDict, attachCommDict):
        
        self.dpmObj = dpm(dpmConnDict)
        self.attachCommDict = attachCommDict

    def start(self):
        
        for partName,  sgDict in self.attachCommDict.items():
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            
            for sgName, devnumArray in sgDict.items():
                sgObj = self.getStorageGroupEntity (sgName)
                
                # attach the storage group to the partition
                try:
                    partObj.attach_storage_group(sgObj)
                    print "Partition", partName, "attach storage group", sgName, "success !"
                except zhmcclient.HTTPError as e:
                    print "Partition", partName, "attach storage group", sgName, "failed !"
                    return None
                
                # update the device numbers
                self.updateDeviceNumbers(sgObj, devnumArray)
            
        print "attachStorageGroups completed ..."

    def getStorageGroupEntity (self, sgName):
        
        try:
            for cpcSg in self.dpmObj.cpc.list_associated_storage_groups():
                if cpcSg.get_property('type') == 'fcp' and cpcSg.get_property('fulfillment-state') == 'complete' and cpcSg.get_property('name') == sgName:
                    return cpcSg
        except zhmcclient.HTTPError as e:
            return None
        
    def updateDeviceNumbers(self, sgObj, devnumArray):
        
        try:
            vsrs = sgObj.virtual_storage_resources.list()
        except zhmcclient.HTTPError:
            return None
        
        if len(devnumArray) == len(vsrs):
            for vsr in vsrs:
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
                    return None
        else:
            print "Number of devnum array not equals to number of vsrs."
            return None

    def getAdapterDesc(self, adapterPortUri):
        adapterUri = adapterPortUri.split('/storage-ports/')[0]
        filter_args = {'object-uri': adapterUri}
        adapterObjs = self.dpmObj.cpc.adapters.list(full_properties=True, filter_args=filter_args)
        return adapterObjs[0].get_property("description")

cf = 'config.cfg'

if __name__ == '__main__':
    
    configComm = configFile(cf)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    attachCommDict = eval(configComm.sectionDict['attachment']['commondict'])
    
    attachment = attachStorageGroups(dpmConnDict, attachCommDict)
    attachment.start()