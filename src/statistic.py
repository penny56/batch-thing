'''
Created on Nov 24, 2019

@author: mayijie
'''

from datetime import *
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
        self.mailSubject = '[T90 statistic] - [' + str(date.today()) + ']'
        self.mailFrom = 'DPM_Auto'
        #self.mailTo = ['mayijie@cn.ibm.com', 'liwbj@cn.ibm.com', 'lbcruz@us.ibm.com', 'jrossi@us.ibm.com']
        self.mailTo = ['w8a3m8t5g8q5q3g0@ibm-systems-z.slack.com', 'mayijie@cn.ibm.com']
        #self.mailTo = ['mayijie@cn.ibm.com']
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
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n"
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
        self.content += "Total " + str(len(stopTimeSpans)) + " partitions was stopped\n"
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
