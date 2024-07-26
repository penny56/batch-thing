'''
Created on Apr. 19, 2023

@author: mayijie
'''

import sys, re, os, time
from configFile import configFile
from dpm import dpm
from log import log
from prsm2api import prsm2api
from urllib.parse import urlencode

class createPartitionLinks:
    def __init__(self, lcdpm, partNameList):
        
        if lcdpm == None:
            # for launch from this case only
            self.dpmObj = dpm(cf)
        else:
            # for launch from partition life cycle object
            self.dpmObj = lcdpm
        self.logger = log.getlogger(self.dpmObj.cpc_name + '-' + self.__class__.__name__)
        self.partNameList = partNameList


    def run(self):

        print ("createPartitionLinks starting >>>")
        
        ctcswitchid = '13'

        # Get the longevity partitions' uri
        cpcID = str(self.dpmObj.cpc.uri).replace('/api/cpcs/','')
        partUris = []
        for partName in self.partNameList:
            partObj = self.dpmObj.cpc.partitions.find(name = partName)
            partUris.append(partObj.uri)

        plTypeSet = {'smc-d', 'hipersockets', 'ctc'}
        plTempl = dict()
        busConns = []

        for plType in plTypeSet:
            plTempl["name"] = self.dpmObj.cpc_name + '-' + plType + '-' + "longevity"
            plTempl["description"] = "Description text."
            plTempl["type"] = plType
            plTempl['cpc-uri'] = str(self.dpmObj.cpc.uri)

            if plType == "smc-d" or plType == "hipersockets":
                for partUri in partUris:
                    busConns.append({'partition-uri': partUri, 'number-of-nics': 1})
                
                # set the connection array
                plTempl["bus-connections"] = busConns
            
            if plType == "ctc":
                plTempl['partitions'] = partUris
                # get the connections
                switchPaths, p2pPaths = createPartitionLinks.identify_ficon_ctc_paths(self.dpmObj, cpcID)
                
                # get the switched path in creating stage, add the p2p path in modify connection stage
                ctcSwitchedAdapterUris = switchPaths[ctcswitchid]
                plTempl['paths'] = [{'adapter-port-uri': ctcSwitchedAdapterUris.pop(), 'connecting-adapter-port-uri': ctcSwitchedAdapterUris.pop()}]
        
            try:
                prsm2api.createPartitionLinks(self.dpmObj.hmc, plTempl)
                self.logger.info(plTempl["name"] + " created successful")
            except Exception as e:
                self.logger.info(plTempl["name"] + " created failed !!!")
                os.system("echo 1 > ./%s" % ("disabled" + "." + self.dpmObj.cpc_name.lower()))
                # Generate a log file dedicate for this failure.
                loggerFailed = log.getlogger(time.strftime('%Y-%m-%d_%H-%M-%S_', time.localtime()) + self.dpmObj.cpc_name + '-' + self.__class__.__name__)
                loggerFailed.info(plTempl["name"] + " partition link create failed. >>")
                loggerFailed.info("<Exception sub-class>: [http_status],[reason]: <message> FORMAT >>")
                loggerFailed.info("{}: {}".format(e.__class__.__name__, e))
                loggerFailed.info("== The longevity script is stopped until you delete the disabled file ==")
            
            plTempl.clear()
            busConns.clear()
            

            
        print ("createPartitionLinks completed ...")


    @staticmethod
    # get this method from CFI unit test cases
    def identify_ficon_ctc_paths(dpmObj, cpcID):
            
        query = urlencode({'adapter-family': 'ficon', 'type': 'fc'})
        FICONAdapters = prsm2api.listAdaptersOfACpc(dpmObj.hmc, cpcID, query)

        switch_path_dict = {}
        p2p_path_dict = {}

        for adapter in FICONAdapters:
            adapter_uri = adapter['object-uri']
            adapter_prop = prsm2api.getAdapterProperties(dpmObj.hmc, adapter_uri)
            port_uri = adapter_prop['storage-port-uris'][0]
            
            endpoint = prsm2api.getStoragePortProperties(dpmObj.hmc, port_uri)
            endpoint_uri = endpoint['connection-endpoint-uri']

            if endpoint_uri is not None:
                endpoints = prsm2api.getStorageSwitchProperties(dpmObj.hmc, endpoint_uri)
                endpoints_class = endpoints['class']

                if endpoints_class == 'storage-switch':
                    domain_id = endpoints['domain-id']
                    
                    if domain_id not in switch_path_dict: 
                        switch_path_dict.update({domain_id : [adapter_uri]})
                        
                    else:
                        switch_path_dict[domain_id].append(adapter_uri)
                elif endpoints_class == 'storage-port':
                    connected_adapter_uri = re.sub('/storage-ports.*','',endpoint_uri)
                
                    if (adapter_uri not in p2p_path_dict) and (adapter_uri not in p2p_path_dict.values()):
                            p2p_path_dict.update({adapter_uri : connected_adapter_uri})
    
        return switch_path_dict, p2p_path_dict


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
        print ("Exit the program for config file read error")
        exit(1)

    partNameList = eval(configComm.sectionDict['partition'][partNameSection])
    
    partObj = createPartitionLinks(None, partNameList)
    partObj.run()

