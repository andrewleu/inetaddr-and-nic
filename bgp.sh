#!/bin/sh
cd /root/ipv6addr
python bgptbl-routeviews.py
python aspath.py
python as_cc.py
