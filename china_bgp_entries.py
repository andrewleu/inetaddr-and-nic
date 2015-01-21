#this script will download the current BGP table of ipv6
# and analyse the neighbors of the AS area
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
from datetime import datetime
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
date=datetime.now()
filename='/home/ipaddr/tables/bgptablev6'+'-'+str(date.date())
g_entries=0; c_entries=0 #global entries and china entries 
print "Proceeding the BGP table of IPv6"
os.system('rm -f %s' % filename) ;#rm the file
print "Downloading"
os.system('wget -q bgp.potaroo.net/v6/as6447/bgptable.txt  -O %s' % filename)
fhandler=  file(filename,'r')
while True :
   line=fhandler.readline();
   if line=='' : #end of the file
         fhandler.close();break
   if len(line.strip().split()[0].split('/'))!=2 :
      continue  #not a route entry
   line=line.strip()
   line=line.replace(",", " ")
   line=line.replace("{",  ""); line=line.replace("}" ,"")
   line=line.split() #from `second field to analyse
   if g_entries==0 :
     g_item=line[0];g_entries=g_entries+1; print line
     g_blocks=0;c_blocks=0 #global ipv6 blocks and china ipv6 blocks
   elif  line[0]==g_item:  #same route entry
     continue
   else :
     g_item=line[0]; g_entries+=1 #next route entry
   blocks=0
   if line[0]!='::/0' :
      mask=48-int(line[0].split('/')[1])
      if mask>=0 :
        blocks=2**mask; 
   asn= line[len(line)-1] #end of the as-path
   if len(asn.split('.'))==2 :  #to process new format ASN
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
   if cur.execute("select cc from inet_num where type='asn' and addr<=%s and addr+block-1>=%s" %(asn, asn)) :
      result=cur.fetchone()[0].lower()
      if result=='cn' :
         c_blocks+=blocks;
         c_entries+=1; print line
   else :
      continue
cur.execute("select sum(power(2,(48-block))) from inet_num where  cc='CN' and type='ipv6'") ;
g_blocks=cur.fetchone()
print "global bgp entries: %s; china bgp entries: %s" % (g_entries, c_entries)
print "china ownes blocks: %s; china ad blocks: %s" %(g_blocks, c_blocks)
cur.execute("insert bgpitems(date,chinabgpitem,totalbgpitem,ratio) values(substring(now(),1,10),%s,%s,%s)" %(c_entries, g_entries, float(c_entries)/g_entries))
cur.execute("insert publish(date,publish, sum,ratio) values(substring(now(),1,10), %s,%s,%s)" %(c_blocks,g_blocks[0],float(c_blocks)/g_blocks[0]))
cur.execute("commit")
cur.close()
conn.close()


      

   


