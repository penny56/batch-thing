'''
Created on Nov 12, 2019

There will have one config file:
vnicComm.cfg ////////////////////////////////
[10dotAccess]

vnicnamesuffix = 10Dot_AccessMode_VLAN1292
vnicdesc = 10 Dot Network Access Mode VLAN 1292
vnicdevnum = 1000
vnicadaptername = OSD 0230 Z25B-17
/////////////////////////////////////////////

partitionName.cfg
/////////////////////////////////////////////
[partGroup]
testdistro = ['part1',
              'part2',
              'part3'
              ]
/////////////////////////////////////////////

This script will create one vNic in each partition in partitionName.cfg

e.g.

python createvNics.py 10dotAccess testdistro


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
            adapter = self.dpmObj.cpc.adapters.find(name = self.vnicCommDict["vnicadaptername"])
        except zhmcclient.NotFound as e:
            pass
        
        # Get the vSwitch
        vswitches = self.dpmObj.cpc.virtual_switches.findall(**{'backing-adapter-uri': adapter.uri})
        vswitch = None
        for vs in vswitches:
            if vs.get_property('port') == int(self.vnicCommDict["vnicadapterport"]):
                vswitch = vs
                break
        
        # Construct the vNic template
        vnicTempl = dict()
        vnicTempl["description"] = self.vnicCommDict["vnicdesc"]
        vnicTempl["device-number"] = self.vnicCommDict["vnicdevnum"]
        vnicTempl["virtual-switch-uri"] = vswitch.uri
        
        for partName in self.partNameList:
            # get the partition
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            
            vnicTempl["name"] = partName + '_' + self.vnicCommDict["vnicnamesuffix"]
            
            # Create the vNic
            try:
                new_vnic = partObj.nics.create(vnicTempl)
            except zhmcclient.HTTPError as e:
                pass

            time.sleep(1)
            
        print "createvNics completed ..."

vnicCommCfg = 'vnicComm.cfg'
partNameCfg = 'partitionName.cfg'

if __name__ == '__main__':
    if len(sys.argv) == 3:
        vnicCommSecName = sys.argv[1]
        partNameSecName = sys.argv[2]
        
    else:
        print ("Please input the vNic section, and partition name array as parameters!\nQuitting....")
        exit(1)
    
    configComm = configFile(vnicCommCfg)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    vnicCommDict = configComm.sectionDict[vnicCommSecName]

    configName = configFile(partNameCfg)
    configName.loadConfig()
    partNameList = eval(configName.sectionDict['partGroup'][partNameSecName])
    
    vNicCreation = createvNics(dpmConnDict, vnicCommDict, partNameList)
    vNicCreation.start()