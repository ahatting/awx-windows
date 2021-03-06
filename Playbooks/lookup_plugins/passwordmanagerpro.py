from __future__ import absolute_import, division, print_function

import json
import os
import urllib

from ansible.errors import AnsibleError
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.urls import open_url
from ansible.plugins.lookup import LookupBase

PMP_URL = ''
PMP_AUTHTOKEN =''

if os.getenv('PMP_URL') is not None:
    PMP_URL = os.environ['PMP_URL']
else:
    raise AnsibleError("Password Manager Pro ERROR - Set PMP Url as environent variable");
if os.getenv('PMP_AUTHTOKEN') is not None:
    PMP_AUTHTOKEN = os.environ['PMP_AUTHTOKEN']
else:
    raise AnsibleError("Password Manager Pro ERROR - Set Authtoken as environent variable");



def getPMPResourceAccountDetails(resourceId,accountId):
    url = '{0}/restapi/json/v1/resources/getResourceAccountDetails?APP_AUTHTOKEN={1}&APP_NAME=ANSIBLE&RESOURCEID={2}&ACCOUNTID={3}'.format(PMP_URL, PMP_AUTHTOKEN, resourceId , accountId)  
    #print (url)
    headers = {'Content-Type':'application/json'}    
    response = open_url(url, method='GET' ,headers=headers,validate_certs=False)
    resp_json = json.loads(response.read().decode('utf-8'))
    if resp_json.get("operation").get("Details"):
       details = resp_json.get("operation").get("Details")
       resourceDetails = details.get("RESOURCEDETAILS")
       accountDetails = json.loads(details.get("ACCOUNTDETAILS"))
       if accountDetails.get("PASSWORD_REASON"):
          raise AnsibleError("Failed to read password from Password Manager Pro : ",accountDetails.get("PASSWORD_REASON"))
       else:						  
          password = accountDetails.get("PASSWORD")   
          return [password]    
    else:
       message = resp_json.get("operation").get("result").get("message")
       raise AnsibleError("Password Manager Pro ERROR -",message)
       
   
class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        resourceName = terms[0]
        accountName = terms[1]
        url = '{0}/restapi/json/v1/resources/getResourceIdAccountId?APP_AUTHTOKEN={1}&APP_NAME=ANSIBLE&RESOURCENAME={2}&ACCOUNTNAME={3}'.format(PMP_URL, PMP_AUTHTOKEN, urllib.parse.quote(resourceName) , urllib.parse.quote(accountName))  
        #print (url)
        headers = {'Content-Type':'application/json'}    
        response = open_url(url, method='GET' ,headers=headers,validate_certs=False)
        resp_json = json.loads(response.read().decode('utf-8'))
        resp_json = resp_json.get("operation")
        if resp_json.get("Details"):
          details = resp_json.get("Details")
          resourceId = details.get("RESOURCEID")
          accountId = details.get("ACCOUNTID")
          password = getPMPResourceAccountDetails(resourceId , accountId)
          return password        
        else:
          message = resp_json.get("result").get("message")
          raise AnsibleError("Password Manager Pro ERROR - %s " % (message))
