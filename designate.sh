#!/bin/bash

echo "$1 Designate services "

for DESIG_SERVICE in `ls /etc/init.d/designate-* | awk -F '/' ' { print $4;}'`; do
        if  [ $DESIG_SERVICE != "designate-agent" ]; then
                service $DESIG_SERVICE $1
        fi
done
