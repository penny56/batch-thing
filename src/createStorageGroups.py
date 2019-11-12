'''
Created on Nov 8, 2019

There will have two config files:
-- partitionComm.cfg: this file will indicate the common parameters like number of processors, memories etc.
-- partitionName.cfg: this file will indicate the partition name, it have several sections
                      each section have a group of names.

@author: mayijie
'''

import sys, time
import zhmcclient
from configFile import configFile
from dpm import dpm

class createStorageGroups:
    def __init__(self, dpmConnDict, sgCommDict, svCommDict, sgNameList):
        
        self.dpmObj = dpm(dpmConnDict)
        self.sgCommDict = sgCommDict
        self.svCommDict = svCommDict
        self.sgNameList = sgNameList

    def start(self):
        
        # construct storage volumes template
        try:
            svsTempl = list()
            for sv in eval(self.svCommDict[self.sgCommDict['sgvolume']]):
                svTempl = dict()
                svTempl['operation'] = 'create'
                if (sv.has_key('storVolDesc') and sv['storVolDesc'] != ''):
                    svTempl['description'] = sv['storVolDesc']
                # for FICON, if model != EAV, the size property will not exist in the dict
                if (sv.has_key('storVolSize')):
                    svTempl['size'] = float(sv['storVolSize'])
                svTempl['usage'] = sv['storVolUse']
                
                # if the sg is for FICON, construct the FICON only properties
                if sv.has_key('storVolModel'):
                    svTempl['model'] = sv['storVolModel']
                if sv.has_key('storVolDevNum'):
                    svTempl['device-number'] = sv['storVolDevNum']
                svsTempl.append(svTempl)
        except  Exception as exc:
            print "[EXCEPTION constructSvTemplate]", exc
            raise exc
        
        # construct storage group template
        try:
            sgTempl = dict()
            sgTempl['cpc-uri'] = self.dpmObj.cpc.uri
            if (self.sgCommDict.has_key('sgdesc') and self.sgCommDict['sgdesc'] != ''):
                sgTempl['description'] = self.sgCommDict['sgdesc']
            sgTempl['type'] = self.sgCommDict['stortype']
            # couldn't convert string to bool
            if (self.sgCommDict['sgshared'] == "True"):
                sgTempl['shared'] = True
            else:
                sgTempl['shared'] = False
            # max-partitions is the property for FCP only
            if (sgTempl['type'] == 'fcp'):
                sgTempl['max-partitions'] = int(self.sgCommDict['maxnumofpars'])
            sgTempl['connectivity'] = int(self.sgCommDict['numofpaths'])
            sgTempl['storage-volumes'] = svsTempl
            sgTempl['email-to-addresses'] = self.sgCommDict['emaillist'].split(',')
        except Exception as exc:
            print "[EXCEPTION constructSgTemplate]", exc
            raise exc

        for sgName in sgNameList:
            sgTempl['name'] = sgName
            
            try:
                self.dpmObj.client.consoles.console.storage_groups.create(sgTempl)
            except (zhmcclient.HTTPError, zhmcclient.ParseError) as e:
                pass
            time.sleep(1)
            
        print "createStorageGroups completed ..."

sgCommCfg = 'sgComm.cfg'
sgNameCfg = 'sgName.cfg'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sgNameSecName = sys.argv[1]
    else:
        print ("Please input the storage group name array as a parameter!\nQuitting....")
        exit(1)
    
    configComm = configFile(sgCommCfg)
    configComm.loadConfig()
    dpmConnDict = configComm.sectionDict['connection']
    sgCommDict = configComm.sectionDict['sgCommon']
    svCommDict = configComm.sectionDict['svCommon']
    
    configName = configFile(sgNameCfg)
    configName.loadConfig()
    sgNameList = eval(configName.sectionDict['sgGroup'][sgNameSecName])
    
    sgCreation = createStorageGroups(dpmConnDict, sgCommDict, svCommDict, sgNameList)
    sgCreation.start()