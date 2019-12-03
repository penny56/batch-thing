'''
Created on Nov 24, 2019

@author: mayijie
'''

from datetime import date
from log import log
import smtplib
from email.mime.text import MIMEText

class statistic:
    
    def __init__(self):
        self.cf = None
        self.logger = log.getlogger(self.__class__.__name__)
        # email
        self.mailHost = '9.12.23.17'
        self.mailSubject = 'T90 statistic'
        self.mailFrom = 'DPM_Auto'
        #self.mailTo = ['mayijie@cn.ibm.com', 'liwbj@cn.ibm.com', 'lbcruz@us.ibm.com', 'jrossi@us.ibm.com']
        self.mailTo = ['mayijie@cn.ibm.com']
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
            self.content += "The average start time span is " + str(int(sum(startTimeSpans)/len(startTimeSpans))) + " seconds\n\n"
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n"
        if len(stopTimeSpans) != 0:
            self.content += "The average start time span is " + str(int(sum(stopTimeSpans)/len(stopTimeSpans))) + " seconds\n\n"

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
            self.content += "The average start time span is " + str(int(sum(startTimeSpans)/len(startTimeSpans))) + " seconds\n\n"
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n"
        if len(stopTimeSpans) != 0:
            self.content += "The average start time span is " + str(int(sum(stopTimeSpans)/len(stopTimeSpans))) + " seconds\n\n"

    # mail the partitions not in active state
    def checkPartitionStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()
        
        failedPartitions = []
        
        for record in records:
            if str(date.today()) in record and "active state" not in record:
                failedPartitions.append(record.split(' - ')[-1])

        mailHeader = '******************************************************************\n'
        mailHeader += '********* Non-active partitions (kvm & lnx partitions) ***********\n'
        mailHeader += '******************************************************************\n\n'

        self.content += mailHeader
        for failedPartition in failedPartitions:
            self.content += failedPartition
        self.content += '\n'   

    # mail the storage groups not in complete state
    def checkStorageGroupsStatus(self, cf):
        
        with open(cf) as fp:
            records = fp.readlines()
        
        pendingStorageGroups = []
        incompleteStorageGroups = []
        
        for record in records:
            if str(date.today()) in record and "complete state" not in record:
                pendingStorageGroups.append(record.split(' - ')[-1])

        mailHeader = '******************************************************************\n'
        mailHeader += '********* Non-complete storage groups ****************************\n'
        mailHeader += '******************************************************************\n\n'
        
        self.content += mailHeader
        for pendingStorageGroup in pendingStorageGroups:
            self.content += pendingStorageGroup
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

    statObj = statistic()
    # mail the partitions start/stop average time span
    statObj.changePartitionStatus('changePartitionStatus.log')
    
    # mail the new created partitions start/stop average time span
    statObj.partitionLifecycle('partitionLifecycle.log')
    
    # mail the stopped partition names
    statObj.checkPartitionStatus('checkPartitionStatus.log')
    
    # mail the storage groups not in complete state
    statObj.checkStorageGroupsStatus('checkStorageGroupsStatus.log')
    
    statObj.sendMail()
    
    print statObj.content
