#!/usr/bin/env python
from designateclient.v2 import client
from designateclient import exceptions
from designateclient import shell

from keystoneclient.auth.identity import generic
from keystoneclient import session as keystone_session

import json
import syslog
import subprocess

def getPayLoad():
	payload_file = open("/etc/consul.d/template/processed/records.json", 'r')
	payload = payload_file.read()
	payload_file.close();
	return json.loads(payload)

def getIDFromRecord(rslist, record):
	for key in range(len(rslist)):
		for i in rslist[key]["records"]:
			if i in record:
				return rslist[key]["id"]

command = ['bash', '-c', '. /home/pascal/source.sh']

proc = subprocess.Popen(command, stdout = subprocess.PIPE)

auth = generic.Password(
	auth_url=shell.env('OS_AUTH_URL'),
	username=shell.env('OS_USERNAME'),
	password=shell.env('OS_PASSWORD'),
	tenant_name=shell.env('OS_TENANT_NAME'))


session = keystone_session.Session(auth=auth)
client = client.Client(session=session)

zoneID = client.zones.list()[0]["id"]
rsList = client.recordsets.list(zoneID)

payload = getPayLoad()

print "Zone id : " + zoneID
syslog.syslog("Adding new nodes to zone : " + zoneID)

for i in range(len(payload)-1):
	pName = payload[i]["name"]
	pRecord = payload[i]["records"]
	
	try:
		rs = client.recordsets.create(zoneID, pName, 'A', pRecord)
		print "New record added: " + rs["id"]
		syslog.syslog("New record added : " + rs["id"])

	except exceptions.Conflict as e:

		print "record already exist..."
		duplicatedID = getIDFromRecord(rsList, pRecord)

		print "Duplicated ID : " + duplicatedID
		syslog.syslog("record already exists...duplicated ID : " + duplicatedID + " - removing recordset")

		print "removing recordset..."
		client.recordsets.delete(zoneID, duplicatedID)
		rs = client.recordsets.create(zoneID, pName, 'A', pRecord)

		print "New record added: " + rs["id"]
                syslog.syslog("New record added : " + rs["id"])
