#!/bin/bash

# Configurations
LDAP_SERVER="ldaps://10.0.0.10:8080"
LDAP_SERVICE_ACC="CN=ldap_user,OU=service_user,DC=company,DC=com"
LDAP_SERVICE_PASSWD="**********"

OS_AUTH_URL="https://10.0.0.10:5000/v3"
OS_USERNAME="ldap_user"
OS_PASSWORD="**********"
OS_TENANT_ADMIN="admin"
OS_DOMAIN_NAME="default"
OS_IDENTITY_API_VERSION="3"
OS_INTERFACE="internal"
OS_USER_DOMAIN_NAME="default"

OPTIONS="--os-auth-url=$OS_AUTH_URL --os-interface=$OS_INTERFACE --os-identity-api-version=$OS_IDENTITY_API_VERSION --os-username=$OS_USERNAME --os-password=$OS_PASSWORD  --os-domain-name=$OS_DOMAIN_NAME --os-user-domain-name=$OS_USER_DOMAIN_NAME"

function search_Group_Tenant () {

        local tenant_name=$1
        members=($(ldapsearch -H $LDAP_SERVER -D $LDAP_SERVICE_ACC -w $LDAP_SERVICE_PASSWD \
                   -b "OU=Groups,OU=service_user,DC=company,DC=com" "(CN=USERS_OPENSTACK_$tenant_name)" member|\
                   grep "^member"|awk -F":" '{print $2}'| awk -F"," '{print $1}'|sed -e 's/^\s//g' -e 's/\s/\_/g'
                ))
}

function set_Members_To_Tenant() {

        local tenant_name=$1
        echo "Project : $tenant_name"
        #For each tenant, look for members
        members=()

        search_Group_Tenant $tenant_name

        echo "Number of members in group USERS_OPENSTACK_${tenant_name^^} : ${#members[@]}";

        # For each memeber, look for its username and openstack ID
        for ((i=0; i < ${#members[@]}; i++))
        do
                #echo "${members[$i]}"
                member=`echo ${members[$i]}|sed 's/\_/ /g'`
                echo $member
                username=$(ldapsearch -H $LDAP_SERVER -D $LDAP_SERVICE_ACC -w $LDAP_SERVICE_PASSWD \
                           -b"OU=service_user,DC=company,DC=com" "($member)" sAMAccountName |\
                           grep "^sAMAccountName"|awk -F":" '{print $2}' | sed -e 's/^\s//g'
                          )
                echo $username

                # Look for openstack ID for user
                user_id=$(openstack $OPTIONS user show $username --domain $OS_DOMAIN_NAME|grep " id"|awk -F"|" '{print $3}'| sed -e 's/^\s//g')
                echo $user_id
                # Add role _member_ and heat owner
                openstack $OPTIONS role add --user $user_id --project $tenant_name _member_ 2>> conflits
                echo "*****"
        done
}

function all_tenants() {
        #Get list of tenants from Openstack
        openstack $OPTIONS project list -c Name -f value --domain $OS_DOMAIN_NAME |while read tenant_name
        do
                echo "Project : $tenant_name"
                if [ "$tenant_name" != "service" ]
                then
                        set_Members_To_Tenant $tenant_name
                fi
        done
}

#Main execution
if [ -z "$1" ]
then
        # No argument, search all Tenants
        read -p "Search all Tenants from Openstack [y|N]? " -n 1 -r
        echo    # move to a new line
        if [[ ! $REPLY =~ ^[Yy]$ ]]
        then
                exit 1
        fi
        echo "Brace yourself, scanning for all tenants..."
        all_tenants
else
        # Check if tenant exist
        openstack $OPTIONS project show $1 --domain $OS_DOMAIN_NAME > /dev/null 2>&1

        if [ $? -eq 0 ]
        then
                set_Members_To_Tenant $1
        else
                echo "Error on tenant name" >&2
        fi
fi

exit 0
