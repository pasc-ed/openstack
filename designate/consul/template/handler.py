#!/usr/bin/env python
from designateclient.v2 import client as desigClient
from designateclient import exceptions
from designateclient import shell

from keystoneclient.auth.identity import generic
from keystoneclient import session as keystone_session
from keystoneclient import client as ksclient

from novaclient import client as novaClient

import json
import syslog
import sys
import base64

# Set up DesignateClient authentication
def getAuthSession( tenant_id ):	
	auth = generic.Password(
        	auth_url  = shell.env( 'OS_AUTH_URL' ),
	        username  = shell.env( 'OS_USERNAME' ),
        	password  = shell.env( 'OS_PASSWORD' ),
	        tenant_id = tenant_id )
	return keystone_session.Session( auth=auth )

# Get JSON data from payload
def getPayLoads():
	for line in sys.stdin:
		return json.loads( line )

# Get Tenant Name
def getTenantName( tenant_id ):
	try:
		ksession = getAuthSession( tenant_id )
		keystone = ksclient.Client( session=ksession )
	
		for t in keystone.tenants.list():
			if t.id == tenant_id:
				return t.name
		return None
	except:
		syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Error getting Tenant Name' )
		return None


# Create new Zone for new tenant
def createZone(client, tenant_id):
	try:
		tenant_name = getTenantName( tenant_id )
		if tenant_name is not None:
			zoneName = tenant_name + '.devstack-os.fr.'
			# Create the zone with Tenant Name	
			zone = client.zones.create( zoneName, email='admin@vsct.fr' )
			return zone[ 'id' ]
		return None
	except exceptions.RemoteError:
		syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Error creating new zone' )
		return None


# Get tenant associated zone
def getZoneID( client, tenant_id ):
	try:
		zones = client.zones.list()
		if not zones:
			return createZone( client, tenant_id )
		else:
			for z in zones:
				if z[ 'project_id' ] == tenant_id:
					return z[ 'id' ]
		return None
	except:
		# No zones found
		syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Error getting zones' )
		return None

# Using nova to get info on floating IP
def dissociateIP( floating_ip ):
	floating_ip = '172.24.4.4'
	# Use Admin Tenant ID for this session
	session = getAuthSession( shell.env( 'OS_TENANT_ID' ) )
	client = novaClient.Client( '2', session=session )
	try:
		fip = client.floating_ips.list()
		if fip is not None:
			for ip in fip:
				print ip.ip
	except novaClient.exceptions.NotFound as nf:
		print "Floating IP : " + floating_ip + " not found on openstack"
	except Exception as e:
		print "Error finding floating IP " + str(type(e))

# Get replicated ID from same zone, if out of zone, rise error
def replaceDuplicatedRecord( zone_id, floating_ip ):
	print "record already exist..."
	rsList = client.recordsets.list( zone_id )
	duplicatedID = getIDFromRecord( rsList, floating_ip )
	if duplicatedID is not None:
		print "removing recordset..."
		client.recordsets.delete( zone_id, duplicatedID )
		rs = client.recordsets.create( zone_id, '*', 'A', [floating_ip] )
		print "IP replaced : " + floating_ip
	else:
		#dissociateIP( floating_ip )
		print "Floating IP not present in zone " + zone_id
		print "IP NOT ADDED!"


# Get Associated ID of recordset
def getIDFromRecord(rslist, record):
	for key in range(len(rslist)):
		for i in rslist[key]['records']:
			if i in record:
				return rslist[key]['id']

# *** MAIN *** #
# Start by getting data from Payload
payloads = getPayLoads()

for p in payloads:
        # Decode data from base64
        data = base64.b64decode( p[ 'Payload' ] )
        try:
		# Retrieve data from Payload
                data = json.loads( base64.b64decode( p[ 'Payload' ] ))
                tenant_id = data[ 'tenant_id' ]
                floating_ip = data[ 'floating_ip' ]
		tenant_name = getTenantName( tenant_id )
		if tenant_name is not None:
			print "Modifying Tenant " + tenant_name

        	        # Set authentication of admin user for this tenant
                	session = getAuthSession( tenant_id )
		        client = desigClient.Client( session=session )
		
			# Get default zone of tenant
                	zone_id = getZoneID( client, tenant_id )

			if zone_id is not None:
		                print "Zone present : " + zone_id
				rs = client.recordsets.create(zone_id, '*', 'A', [floating_ip])
				print "New IP added : " + floating_ip
			else:
				syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Zone ID not found for tenant_id: ' + tenant_id)
		else:
			print "Tenant Not Found for id : " + tenant_id
			syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Tenant Not Found : ' + tenant_id)
		print "------------"
	except exceptions.Conflict:
		replaceDuplicatedRecord( zone_id, floating_ip )
		print "------------"
	except Exception as e:
		syslog.syslog( syslog.LOG_ERR, '[CONSUL_HANDLER] Payload error for ' + str( data ) + " : " + str( type( e )) + " : " + str( e ))
		continue
