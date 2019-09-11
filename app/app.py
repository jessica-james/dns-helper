#!/usr/bin/env python3

import requests
import logging
from os import environ
import json
from cprint import *

# import http logging
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1
logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# Define Python Variables from Shell Environment Variables
record = environ.get('RECORD', 'test')
crate_host = environ.get('HOST_UUID', 'test')
dnsapi_endpoint = environ.get('DNS_MGMT_ENDPOINT', 'http://dnsmgmt-service.prod-dnsmgmt:9000')
action_is = environ.get('ACTION_TO_TAKE', 'validate')

# Code


class DNSManipulation:
    allowed_actions = ['validate', 'create', 'delete', 'update']

    def __init__(self, host, dnsRecord, action, dnsmgmt='http://dnsmgmt-service.prod-dnsmgmt:9000', tries=0):
        if action not in DNSManipulation.allowed_actions:
            raise ValueError(f"The only allowed actions for action are {DNSManipulation.allowed_actions}, you gave the action {action}")
        self.action = action
        self.dnsmgmt = dnsmgmt
        self.host = host
        self.retries = tries
        self.dnsRecord = dnsRecord
        self.success = False
        # define our attributes when action is create
        if self.action == 'create':
            self.createurl = ''.join([x for x in (dnsmgmt, "/record/")])
            self.headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            self.payload = [
                {
                    'domainName': self.dnsRecord,
                    'value': self.host,
                    'regions': []
                }
            ]
            self.req1 = requests.Request('POST', self.createurl, headers=self.headers, data=json.dumps(self.payload))
            self.s1 = requests.Session()
            self.prep1 = self.s1.prepare_request(self.req1)
            self.resp1 = ''
# define our attributes when action is update
        elif self.action == 'update':
            self._success1 = False
            self._success2 = False
            self.url = ''.join([x for x in (dnsmgmt, "/record/", dnsRecord)])
            self.createurl = ''.join([x for x in (dnsmgmt, "/record/")])
            self.headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            self.payload = [
                {
                    'domainName': self.dnsRecord,
                    'value': self.host,
                    'regions': []
                }
            ]
            self.req1 = requests.Request('DELETE', self.url)
            self.s1 = requests.Session()
            self.prep1 = self.s1.prepare_request(self.req1)
            self.resp1 = ''
            self.req2 = requests.Request('POST', self.createurl, headers=self.headers, data=json.dumps(self.payload))
            self.s2 = requests.Session()
            self.prep2 = self.s2.prepare_request(self.req2)
            self.resp2 = ''
# define our attributes when action is validate
        elif self.action == 'validate':
            self.url = ''.join([x for x in (dnsmgmt, "/record/", dnsRecord)])
            self.req1 = requests.Request('GET', self.url)
            self.s1 = requests.Session()
            self.prep1 = self.s1.prepare_request(self.req1)
            self.resp1 = ''
# define our attributes when action is delete
        elif self.action == 'delete':
            self.url = ''.join([x for x in (dnsmgmt, "/record/", dnsRecord)])
            self.req1 = requests.Request('Delete', self.url)
            self.s1 = requests.Session()
            self.prep1 = self.s1.prepare_request(self.req1)
            self.resp1 = ''

    def validate(self):
        if self.action != 'validate':
            pass
        else:
            while self.success == False and self.retries < 5:
                cprint.info(f"Checking to see if the DNS entry {self.dnsRecord} exists")
                self.resp1 = self.s1.send(self.prep1).status_code
                if self.resp1 == 200:
                    self.success = True
                    return cprint.ok(f"The domain {self.dnsRecord} exists")
                elif self.resp1 == 404:
                    self.success = True
                    return cprint.ok(f"The domain {self.dnsRecord} does not exist")
                elif self.resp1 != 404 or 200:
                    cprint.warn(f"The check of Domain {self.dnsRecord} failed with {self.resp1}")
                    self.resp1 = self.s1.send(self.prep1).status_code
                    self.retries += 1

    def create(self):
        if self.action != 'create':
            pass
        else:
            while self.success == False and self.retries < 5:
                cprint.info(f"Trying to create the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                self.resp1 = self.s1.send(self.prep1).status_code
                if self.resp1 == 200:
                    self.success = True
                    return cprint.ok(f"Successfully created the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                else:
                    cprint.warn(f"Failed to create the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                    self.resp1 = self.s1.send(self.prep1).status_code
                    self.retries += 1

    def delete(self):
        if self.action != 'delete':
            return
        else:
            while self.success == False and self.retries < 5:
                cprint.info(f"Trying to delete the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                self.resp1 = self.s1.send(self.prep1).status_code
                if self.resp1 == 200:
                    self.success = True
                    return cprint.ok(f"Successfully deleted the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                else:
                    cprint.warn(f"Failed to delete the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                    self.resp1 = self.s1.send(self.prep1).status_code
                    self.retries += 1
# Update is not currently supported by DNS management, so we will delete and then create if the record exists

    def update(self):
        if self.action != 'update':
            return
        else:
            while self.success == False and self.retries < 5:
                cprint.info(f"Trying to update the pointer record for domain '{self.dnsRecord}' with new value '{self.host}'")
                self.resp1 = self.s1.send(self.prep1).status_code
                if self.resp1 == 200:
                    self._success1 = True
                    cprint.ok(f"Successfully deleted the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                else:
                    cprint.warn(f"Failed to delete the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                    self.resp1 = self.s1.send(self.prep1).status_code
                    self.retries += 1
                    # if the deletion is successful try to create the record
                self.retries = 0
                while self._success1 == True and self._success2 == False and self.retries < 5:
                    cprint.info(f"Trying to create the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                    self.resp2 = self.s2.send(self.prep2).status_code
                    if self.resp2 == 200:
                        self._success2 = True
                        self.success = True
                    else:
                        cprint.warn(f"Failed to create the domain '{self.dnsRecord}' with pointer record '{self.host}'")
                        self.resp2 = self.s2.send(self.prep2).status_code
                        self.retries += 1
            if self.success == True:
                return cprint.ok(f"Successfully updated the domain '{self.dnsRecord}' with new value '{self.host}'")


request1 = DNSManipulation(crate_host, record, 'validate', dnsapi_endpoint)
request1.validate()
request2 = DNSManipulation(crate_host, record, action_is, dnsapi_endpoint)


def main():
    # Will only call create if the record doesn't exist
    if request1.resp1 != 200 and request2.action == 'create':
        return request2.create()
    elif request1.resp1 == 200 and request2.action == 'create':
        return cprint.warn(f"Can\'t create the record {request1.dnsRecord}, it already exists")
    # Will only delete the record if it exists (duh)
    elif request1.resp1 == 200 and request2.action == 'delete':
        return request2.delete()
    elif request1.resp1 != 200 and request2.action == 'delete':
        return cprint.warn(f"Can\'t delete the record {request2.dnsRecord}, it doesn\'t exist")
    # Will only update a record if it exists already
    elif request1.resp1 == 200 and request2.action == 'update':
        return request2.update()
    elif request1.resp1 != 200 and request2.action == 'update':
        return cprint.warn(f"Can\'t update the record for domain '{request2.dnsRecord}', the record doesn\'t exist!")


print(main())









