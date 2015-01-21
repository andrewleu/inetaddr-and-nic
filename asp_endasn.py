#insert IPv6 addr block and last as in to DB
# and analyse the neighbors of the AS area
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
filename='/home/ipaddr/bgptablev6.txt'
g_entries=0; c_entries=0 #global entries and china entries 
print "Proceeding the BGP table of IPv6"
os.system('rm -f %s' % filename) ;#rm the file
os.system('wget -q bgp.potaroo.net/v6/as6447/bgptable.txt  -O %s' % filename)
fhandler=  file(filename,'r')
while True :
   line=fhandler.readline();
   if line=='' : #end of the file
         fhandler.close(); break
   if len(line.strip().split()[0].split('/'))!=2 :
      continue  #not a route entry
   line=line.strip()
   line=line.replace(",", " ")
   line=line.replace("{",  ""); line=line.replace("}" ,"")
   line=line.split() #from `second field to analyse
   asn= line[len(line)-1] #end of the as-path
   if len(asn.split('.'))==2 :
      asn=int(asn.split('.')[0])*65536+int(asn.split('.')[1])
   else :
     error=0
     try :
       asn=int(asn)
     except Exception, e:
       print e
       error=1
   if error :
      continue
   try:
     cur.execute("insert asp(addr,asn) values('%s','%s')" %(line[0],asn))
   except Exception, e :
     #print e;print line; 
     pass
   finally :
     cur.execute("commit")
cur.close()
conn.close()
