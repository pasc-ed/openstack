# Python script to create NameServer for
# Designate 2.0.0
# Author        : Pascal Edouard
# Date          : March 2016

import os
import json
import requests

keystone_url    = "http://10.0.4.15:5000/v2.0"
designate_url   = "http://10.20.0.3:9001/v2"

payload_auth    = '{ "auth": {                          \
                        "tenantName": "admin",          \
                        "passwordCredentials": {        \
                                "username": "admin",    \
                                "password": "nova"      \
                        }}}'

headers         = { 'content-type' : 'application/json',
                    'accept'       : 'application/json'
                  }

def getToken():
    token = requests.post(keystone_url + "/tokens", data=payload_auth, headers=headers)
    token_file = open("token_file", 'w+')
    token_file.write(token.text)
    token_file.close()
    return json.loads(token.text)

def getPayload():
    payload_file = open("/etc/consul.d/templates/processed/designate.payload", 'r')
    payload = payload_file.read()
    payload_file.close();
    return json.loads(payload)

def getTokenFromFile():
    token_file = open("token_file", 'r')
    data = token_file.read()
    token_file.close()
    return json.loads(data)

def getZones():
    response = requests.get(designate_url + "/zones", headers=headers)
    #print response.text
    return json.loads(response.text)["zones"][0]["id"]

# Get Token
if os.path.exists("token_file"):
    data = getTokenFromFile()
    #print "Token exists from file"
else:
    data = getToken()

headers = { 'content-type' : 'application/json',
            'accept'       : 'application/json',
            'x-Auth-Token' : data["access"]["token"]["id"]
          }

zone_id = getZones()
payload = getPayload()

print payload
print "**********"
for i in range(len(payload)-1):
	print "Name : " + payload[i]["name"]
	print "Address : " + payload[i]["records"][0]
	print "**********"

#response = requests.post(designate_url + "/zones/" + zone_id + "/recordsets", data=payload, headers=headers)

#print response.text
