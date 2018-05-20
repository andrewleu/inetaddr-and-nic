# all the as in china advertised in ipv6 bgp. check the owner of the certain AS 
# it is editted by 2015 09
#!/bin/python
# -*- coding: UTF-8 -*-
#calculcate a month for downloading speed, please revise ymd first
import sys
import MySQLdb as mysql
import re
import select
import os
import random
global yandm;
global day
global ymd
import socket
from datetime import timedelta, datetime 
dbaddr="127.0.0.1"
tab=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat',charset='utf8')
cur_tab=tab.cursor();
cur_tab.execute("set names 'utf8'")
reload(sys)
sys.setdefaultencoding('UTF-8')
cur_tab.execute("select * from asncn");
list=cur_tab.fetchall()
list=list[118:]
for item in list :
   if item[1].find('.') !=-1 :
       asn=int(item[1].split('.')[0])*65536+int(item[1].split('.')[1])
   else :
       asn=int(item[1])
   try:   #try to connect ipv6 first
        socket.setdefaulttimeout(30)   #30 secs to timeout
        sock=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.connect(('whois.apnic.net',43))
   except socket.error:
        try:  #then ipv4
           sock.close()
           sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.connect(('whois.apnic.net',43))
        except socket.error :
           sock.close(); print 'socket error... '
           print sys.exc_info()
   query_addr='as'+str(asn)
   sock.send(query_addr)
   response=''
   while True :
        try:
            cache =sock.recv(2048)
        except socket.error:
            sock.close()
            print 'error 2'
            print sys.exc_info()
            cur_tab.execute('commit')
            cache=''
            break
        response+=cache
        if cache == '' :
              break
   response=response.replace("'",'').replace('"','')
   response=response.replace('\n','|').replace('\t',' ')
   response=response.replace('||',"|").replace("||","|")
   p=re.compile(r'\s+')
   response=p.sub(r' ', response) ;print response
   response=response.replace('\xa3',' ').replace('\xac','')
   #p=re.compile(r'^\s|^"|"|\W+');
   #//response=p.sub(r'',response)
   #//print response
   init=response.rfind('as-block:')
   cur_tab.execute("update asncn set com='%s' where id='%s'" % (response[init:init+2048], item[0]))
   cur_tab.execute("commit")
   sock.close()
cur_tab.close()
exit()
