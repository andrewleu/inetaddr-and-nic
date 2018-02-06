#this script will use the current BGP table 
# and analyse the neighbors of the AS area
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
import datetime
date=str(datetime.datetime.now())
#-datetime.timedelta(days=1))
date_format=date.split()[0]
date=date.replace('-','').split()[0]
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
type='ipv6'
filename='./bgptbl/'+'bgp'+date
no=0; #lines number
cur.execute("select asn, locked from aspath where type='cnt'")
# asn to store the times for checking ipv6 aspath
ftch=cur.fetchone()
cnt=int(ftch[0])
print "Proceeding the BGP table of IPv6"
"""
lck=ftch[1]
lck=0
if lck==0 :
  os.system('rm -f %s' % filename) ;#rm the file
  print "Downloading"
  os.system('wget -q bgp.potaroo.net/v6/as6447/bgptable.txt  -O %s' % filename)
  cnt=int(ftch[0])+1
  cur.execute("update aspath set asn = '%s', locked=1 where type='cnt'" % str(cnt))  
  cur.execute("commit")
  cur.execute("update aspath set locked=0 where type='%s'" % type) #unlock all ipv6 entry
  cur.execute("commit")
 # use type=cnt entry to store check times asn for ipv6 nextasn for ipv4
"""
fhandler=     file(filename,'r')
cur.execute("update aspath set locked=0 where type='%s'" % type)
cur.execute("commit")
try:
  while True :
    line=fhandler.readline()
    if line.find('::/0')!=-1 :
       continue
    no+=1
#   print no
    if line=='' :
         break
    if line.strip()[0]==' ' :
      continue 
    line=line.strip()
    line=line.replace(",", " ")
    line=line.replace("{",  ""); line=line.replace("}" ,"")
    line=line.split()[1:] #from `second field to analyse
    i=0
   #print str(no)+' '+str(line)
    while i < len(line)- 1:
        #if no%10000==0 :
        #   print line[i]+":"+line[i+1]
        if line[i] != line[i+1] : # asn=asn 
           cur.execute('begin')    
           if cur.execute("select id, connect,locked  from aspath where type='%s' and `asn`='%s' \
           and nextasn='%s'  " % (type,line[i],line[i+1]))== 0 :
           # inserting NEW entry
             cur.execute("insert aspath(type,asn, nextasn,1stins, `up_date`,locked) \
             value('%s','%s','%s',substring(now(),1,10),substring(now(),1,10), 0)" \
             % (type,line[i],line[i+1]))
             #print line[i], line[i+1]
           else : #update previous records
              fetch=cur.fetchone()
              if fetch[2]==1 :  # line has been updated
                  i=i+1
                  continue
              as1=line[i];as2=line[i+1]
              if line[i].find('.')>0 :
                 as1=str(int(line[i].split('.')[0])*65536+int(line[i].split('.')[1]))
              if line[i+1].find('.')>0 :
                  as2=str(int(line[i+1].split('.')[0])*65536+int(line[i+1].split('.')[1]))
              if cur.execute("select CC from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s \
              order by date desc" % (as1, as1)) !=0 :
                 fromAS=cur.fetchone()[0];
              else :
                   fromAS='-'
              if cur.execute("select CC from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s \
              order by date desc" % (as2, as2))!=0 :
                   toAS=cur.fetchone()[0];
              else :
                   toAS='-'
              cur.execute("select id from aspath where id=%s for update" % fetch[0])
              cur.execute("update aspath set orias= '%s',desas='%s',locked=1, up_date=substring(now(),1,10) \
              where id=%s " % (fromAS, toAS, fetch[0]))
        i+=1
        if fetch[0]%10000 ==0 :
           print fetch[0], as1, fromAS, as2, toAS
        # update Previous entry
    cur.execute('commit')
except BaseException, e :
     print "Error :"
     print e
     cur.execute("commit")
fhandler.close()
#this version will test if the connection is stable,and the region
"""
try : 
 while True :  #to check the regions for both ends of the aspath
   fromAS='-'; toAS='-'
   if cur.execute("select id,asn,nextasn from aspath where locked=0  order by rand() limit 2000") !=0 :
    lines=list(cur.fetchall()); 
    for line in lines :
      line=list(line)
      if line[1].find('.')>0 : #long ASN some noted as 3.9
        line[1]= str( int(line[1].split('.')[0])*65536+int(line[1].split('.')[1]))
      if cur.execute("select CC  from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s order by date desc" % (line[1],line[1])) !=0 :
        fromAS=cur.fetchone()[0]; 
      else :
        fromAS='-'
      if line[2].find('.')>0 :
        line[2]= str( int(line[2].split('.')[0])*65536+int(line[2].split('.')[1]))
      if cur.execute("select CC from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s order by date desc" % (line[2],line[2]))!=0 :
         toAS=cur.fetchone()[0];  
      else :
         toAS='-'
         #print '%s, %s' %(line[1],line[2])
     #note=list(fromAS)[0]+'-'+list(toAS)[0]; #print note 
      cur.execute("select id from aspath where id=%s for update" % line[0])
      cur.execute("update aspath set orias= '%s',desas='%s',locked=1, up_date=substring(now(),1,10) \
      where id=%s " % (fromAS, toAS, line[0]))
    cur.execute("commit")
   else :
     break  #end
   if line[0]%100==0 :
     print fromAS, toAS
except BaseException, e :
  print 'ERROR:'
  print e
  cur.execute("commit")
"""
print "updating database "+str(no)
cur.execute("update aspath set locked=0 where type='cnt'")  
#cur.execute("insert entries(type,entries,date) value('%s','%s',substring(now(),1,10)" % (type,no))
cur.execute("commit")
#unlock the table
cur.close()
conn.close()
"""
CREATE TABLE `aspath` (
  `id` bigint(16) NOT NULL AUTO_INCREMENT,
  `type` varchar(8) NOT NULL DEFAULT '',
  `asn` varchar(16) NOT NULL DEFAULT '',
  `oriAS` varchar(3) DEFAULT NULL,
  `nextasn` varchar(16) NOT NULL DEFAULT '',
  `desAS` varchar(3) DEFAULT NULL,
  `connect` int(8) NOT NULL DEFAULT '1',
  `locked` bigint(2) NOT NULL DEFAULT '1',
  `1stins` date DEFAULT '0000-00-00',
  `up_date` date DEFAULT NULL,
  PRIMARY KEY (`type`,`asn`,`nextasn`),
  KEY `asn` (`asn`,`nextasn`),
  KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=226936 DEFAULT CHARSET=utf8;

"""      

   


