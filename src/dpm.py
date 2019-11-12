'''
Created on Jan 16, 2019

@author: mayijie
'''

import sys
import zhmcclient
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

class dpm():
    def __init__(self, conSection):
        self.hmc_host = conSection["hmc"]
        self.__user_id = conSection["uid"]
        self.__user_psw = conSection["psw"]
        self.cpc_name = conSection["cpc"]

        self.session = zhmcclient.Session(self.hmc_host, self.__user_id, self.__user_psw)
        self.client = zhmcclient.Client(self.session)
        self.cpc = self.client.cpcs.find_by_name(self.cpc_name)
        self.partition = None
        
