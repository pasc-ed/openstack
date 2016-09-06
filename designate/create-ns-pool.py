# Python script to create NameServer for Designate api 2
# Author        : Pascal Edouard
# Date          : March 2016

import os
import json
import requests


keystone_url    = "http://10.0.0.10:5000/v2.0"
designate_url   = "http://10.0.0.10:9001/v2"

payload_auth    = '{ "auth": {                          \
                        "tenantName": "admin",          \
                        "passwordCredentials": {        \
                                "username": "admin",    \
                                "password": "nova"      \
                        }}}'

payload_ns      = '{ "name": "DevStack-OS Example Pool",   \
                     "ns_records": [{                      \
                        "hostname": "ns1.devstack-os.fr.", \
                        "priority": 1 }]}'

headers         = { 'content-type' : 'application/json',
                    'accept'       : 'application/json'
                  }

def getToken():
    token = requests.post(keystone_url + "/tokens", data=payload_auth, headers=headers)
    return json.loads(token.text)

# Get Token
data = getToken()

headers = { 'content-type' : 'application/json',
            'accept'       : 'application/json',
            'x-Auth-Token' : data["access"]["token"]["id"]
          }

response = requests.post(designate_url + "/pools", data=payload_ns, headers=headers)
#print response.text
#print "\n"
# Pool ID to set in /etc/designate/designate.conf
print "New pool ID : " + json.loads(response.text)["id"]
