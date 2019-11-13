'''
Created on Nov 12, 2019

Configuration include two sections in config.cfg file
-- [connection] section include the HMC and CPC information
-- [network] section include the created vNic parameters
   -- <commondict> dictionary include the vNics common parameters
      like vNic name, device number, description and adapter information
   -- <partition name> array include the partitions' name which the vNics will be created in
      this option must be indicated in the command line as a parameter

e.g.
python createvNics.py rhel 

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm

class createvNics:
    def __init__(self, dpmConnDict, vnicCommDict, partNameList):
        
        self.dpmObj = dpm(dpmConnDict)
        self.vnicCommDict = vnicCommDict
        self.partNameList = partNameList

    def start(self):
        
        # Check if the adapter exist.
        try:
            adapter = self.dpmObj.cpc.adapters.find(name = self.vnicCommDict["adaptername"])
        except zhmcclient.NotFound as e:
            pass
        
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
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            
            vnicTempl["name"] = partName + '_' + self.vnicCommDict["namesuffix"]
            
            # Create the vNic
            try:
                new_vnic = partObj.nics.create(vnicTempl)
                print "vNic", vnicTempl["name"], "in partition", partName, "created success !"
            except zhmcclient.HTTPError as e:
                print "vNic", vnicTempl["name"], "in partition", partName, "created failed !"
            time.sleep(1)

        print "createvNics completed ..."

cf = 'config.cfg'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        vnicSection = sys.argv[1]
        
    else:
        print ("Please input the vNic creation model as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(cf)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    vnicCommDict = eval(configComm.sectionDict['network']['commondict'])
    partNameList = eval(configComm.sectionDict['network'][vnicSection])

    vNicCreation = createvNics(dpmConnDict, vnicCommDict, partNameList)
    vNicCreation.start()