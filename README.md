# openstack-designate

* create-ns-pool.py

Register a nameserver using designate api v2 using :

```
{
	"name": "DevStack-OS Example Pool",
	"ns_records": [{
		"hostname": "ns1.devstack-os.fr.",
		"priority": 1
     }]
}
```

* designate.sh Usefull script to launch service commands on all designate services (start, stop, status, restart) :
  * designate-api
  * designate-central
  * designate-mdns
  * designate-pool-manager
