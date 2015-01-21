#!/bin/sh
cd /root/ipv6addr
python threading.locktbl.py
python aspath.py
python nic.py
python internicv2.py
