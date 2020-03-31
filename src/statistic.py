'''
Created on Nov 24, 2019

@author: mayijie
'''

from datetime import *
from datetime import date
from configFile import configFile
from log import log
import sys
import smtplib
from email.mime.text import MIMEText

class statistic:
    
    def __init__(self):
        self.cf = cf
        self.logger = log.getlogger(configComm.sectionDict['connection']['cpc'] + '-' + self.__class__.__name__)
        # email
        #self.mailHost = '9.12.23.17'
        # use the IBM official smtp server
        self.mailHost = 'na.relay.ibm.com'
        self.mailSubject = '[' + configComm.sectionDict['connection']['cpc'] + ' statistic] - [' + str(date.today()) + ']'
        self.mailFrom = 'DPM_Auto'
        #self.mailTo = ['mayijie@cn.ibm.com']
        self.mailTo = ['w8a3m8t5g8q5q3g0@ibm-systems-z.slack.com']
        self.content = ''

    def changePartitionStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()

        startTimeSpans = []
        stopTimeSpans = []

        for record in records:
            if str(date.today()) in record and "start successful" in record:
                startTimeSpans.append(int(record.split(' ')[-1].strip()))
            if str(date.today()) in record and "stop successful" in record:
                stopTimeSpans.append(int(record.split(' ')[-1].strip()))
        
        mailHeader = '******************************************************************\n'
        mailHeader += '********* Partitions start/stop time span ************************\n'
        mailHeader += '******************************************************************\n\n'

        self.content += mailHeader
        self.content += "Total " + str(len(startTimeSpans)) + " partitions was started\n"
        if len(startTimeSpans) != 0:
            self.content += "The maximum start time span is " + str(max(startTimeSpans)) + " seconds\n"
            self.content += "The average start time span is " + str(int(sum(startTimeSpans)/len(startTimeSpans))) + " seconds\n"
            self.content += "The minimum start time span is " + str(min(startTimeSpans)) + " seconds\n\n"
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n\n"
        if len(stopTimeSpans) != 0:
            self.content += "The maximum stop time span is " + str(max(stopTimeSpans)) + " seconds\n"
            self.content += "The average stop time span is " + str(int(sum(stopTimeSpans)/len(stopTimeSpans))) + " seconds\n"
            self.content += "The minimum stop time span is " + str(min(stopTimeSpans)) + " seconds\n\n"

    def partitionLifecycle(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()

        startTimeSpans = []
        stopTimeSpans = []

        for record in records:
            if str(date.today()) in record and "start successful" in record:
                startTimeSpans.append(int(record.split(' ')[-1].strip()))
            if str(date.today()) in record and "stop successful" in record:
                stopTimeSpans.append(int(record.split(' ')[-1].strip()))
        
        mailHeader = '******************************************************************\n'
        mailHeader += '********* (new created) Partitions start/stop time span **********\n'
        mailHeader += '******************************************************************\n\n'

        self.content += mailHeader
        self.content += "Total " + str(len(startTimeSpans)) + " partitions was started\n"
        if len(startTimeSpans) != 0:
            self.content += "The maximum start time span is " + str(max(startTimeSpans)) + " seconds\n"
            self.content += "The average start time span is " + str(int(sum(startTimeSpans)/len(startTimeSpans))) + " seconds\n"
            self.content += "The minimum start time span is " + str(min(startTimeSpans)) + " seconds\n\n"
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n\n"
        if len(stopTimeSpans) != 0:
            self.content += "The maximum stop time span is " + str(max(stopTimeSpans)) + " seconds\n"
            self.content += "The average stop time span is " + str(int(sum(stopTimeSpans)/len(stopTimeSpans))) + " seconds\n"
            self.content += "The minimum stop time span is " + str(min(stopTimeSpans)) + " seconds\n\n"

    # mail the partitions not in active state
    # For checking function, we not only check today, but check the same hour within today
    def checkPartitionStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()
        
        nonActiveParts = []
        # dateHour like '2020-03-10 15'
        dateHour = str(datetime.now()).split(':')[0]
        for record in records:
            if dateHour in record and "active state" not in record:
                nonActiveParts.append(record.split(' - ')[-1])

        # remove the redundant records
        nonActiveParts = list(set(nonActiveParts))

        mailHeader = '******************************************************************\n'
        mailHeader += '********* Non-active partitions (kvm & lnx partitions) ***********\n'
        mailHeader += '******************************************************************\n\n'

        self.content += mailHeader
        for nonActivePart in nonActiveParts:
            self.content += nonActivePart
        self.content += '\n'   

    # mail the storage groups not in complete state
    # For checking function, we not only check today, but check the same hour within today
    def checkStorageGroupsStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()
        
        nonCompleteSgs = []
        # dateHour like '2020-03-10 15'
        dateHour = str(datetime.now()).split(':')[0]
        for record in records:
            if dateHour in record and "in complete state" not in record:
                nonCompleteSgs.append(record.split(' - ')[-1])

        # remove the redundant records
        nonCompleteSgs = list(set(nonCompleteSgs))

        mailHeader = '******************************************************************\n'
        mailHeader += '********* Non-complete storage groups ****************************\n'
        mailHeader += '******************************************************************\n\n'
        
        self.content += mailHeader
        for nonCompleteSg in nonCompleteSgs:
            self.content += nonCompleteSg
        self.content += '\n'


    # Adapter status: 
    #         Active            Indicates that the adapter is operating normally.
    #         Not active        Indicates that the adapter is not operating.
    #         Service           Indicates that the adapter requires service.
    #         Exceptions        Indicates that at least one adapter on the system is not operating.
    #
    # Adapter state: Online | Reserved | Standby
    def checkAdaptersStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()
        
        networkNotInActives = []
        storageNotInActives = []
        cryptoNotInActives = []
        
        # dateHour like '2020-03-10 15'
        dateHour = str(datetime.now()).split(':')[0]
        for record in records:
            if dateHour in record and record.split(' | ')[1] in ['osd', 'osm', 'roce'] and record.split(' | ')[2] != "active" and record.split(' | ')[4] != "\n":
                networkNotInActives.append(record.split(' - ')[-1])
            if dateHour in record and record.split(' | ')[1] in ['fcp', 'fc', 'nvme'] and record.split(' | ')[2] != "active" and record.split(' | ')[4] != "\n":
                storageNotInActives.append(record.split(' - ')[-1])
            if dateHour in record and record.split(' | ')[1] in ['crypto'] and record.split(' | ')[2] != "active":
                cryptoNotInActives.append(record.split(' - ')[-1])
        
        # remove the redundant records
        networkNotInActives = list(set(networkNotInActives))
        storageNotInActives = list(set(storageNotInActives))
        cryptoNotInActives = list(set(cryptoNotInActives))
        
        mailHeader = '******************************************************************\n'
        mailHeader += '********* Not in Active Status adapters **************************\n'
        mailHeader += '******************************************************************\n\n'
        
        self.content += mailHeader
        self.content += 'network:\n'
        self.content += 'ID  | type | status     | state    | Descripton\n'
        for networkNotInActive in networkNotInActives:
            self.content += networkNotInActive
        self.content += '\n'

        self.content += 'storage:\n'
        self.content += 'ID  | type | status     | state    | Descripton\n'
        for storageNotInActive in storageNotInActives:
            self.content += storageNotInActive
        self.content += '\n'
        
        self.content += 'crypto:\n'
        self.content += 'ID  | type   | status     | state    | Descripton\n'
        for cryptoNotInActive in cryptoNotInActives:
            self.content += cryptoNotInActive
        self.content += '\n'
        
    def sendMail(self):
        
        # construct the mail parameters
        msg = MIMEText(self.content, 'plain', 'utf-8')
        msg['From'] = self.mailFrom
        msg['To'] = ','.join(self.mailTo)
        msg['Subject'] = self.mailSubject
        
        # send the mail
        try:
            smtpObj = smtplib.SMTP(self.mailHost, 25)
            smtpObj.sendmail(self.mailFrom, self.mailTo, msg.as_string())
            smtpObj.quit()
        except Exception as e:
            print "Error..mail.."
        
if __name__ == '__main__':

    if len(sys.argv) == 2:
        cf = sys.argv[1]
    else:
        print ("Please input the config file as a parameter!\nQuitting....")
        exit(1)

    try:
        configComm = configFile(cf)
        configComm.loadConfig()
    except Exception:
        print "Exit the program for config file read error"
        exit(1)    
    
    statObj = statistic()
    
    # mail the stopped partition names
    statObj.checkPartitionStatus(configComm.sectionDict['connection']['cpc'] + '-' + 'checkPartitionStatus.log')
    
    # mail the storage groups not in complete state
    statObj.checkStorageGroupsStatus(configComm.sectionDict['connection']['cpc'] + '-' + 'checkStorageGroupsStatus.log')
    
    # mail the partitions start/stop average time span
    statObj.changePartitionStatus(configComm.sectionDict['connection']['cpc'] + '-' + 'changePartitionStatus.log')
    
    # mail the new created partitions start/stop average time span
    statObj.partitionLifecycle(configComm.sectionDict['connection']['cpc'] + '-' + 'partitionLifecycle.log')
    
    # mail the adapters not in Active status
    statObj.checkAdaptersStatus(configComm.sectionDict['connection']['cpc'] + '-' + 'checkAdaptersStatus.log')
    
    statObj.sendMail()
    
    print statObj.content
