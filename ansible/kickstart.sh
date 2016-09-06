#!/usr/bin/env bash

set -e

yum update -y

yum install \
  python-setuptools \
  python-devel \
  openssl-devel \
  sudo \
  libffi-devel \
  git \
  gcc \
  gcc-c++ \
  make \
  openssl-devel \
  libxml2 \
  libxml2-devel \
  libxslt \
  libxslt-devel \
  perl-devel \
  automake \
  -y

echo "Installing pip via easy_install"
for i in 1 2 3 4 5; do easy_install pip && break || sleep 2; done

echo "Installing correct python crypto libs"
pip install -U pyopenssl ndg-httpsclient pyasn1

echo "Installing ansible via pip"
pip install -U pip ansible

mkdir -p /etc/ansible/

echo "Installing shade module via pip"
pip install -U shade

echo "Installing Openstack Client via pip"
pip install -U python-openstackclient

echo "Installing Neutron Client via pip"
pip install -U python-neutronclient

echo "Installing Keystone Client via pip"
pip install -U python-keystoneclient

echo "Installing ldap utlis"
yum install openldap-clients -y
