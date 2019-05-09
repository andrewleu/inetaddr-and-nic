#this script will use the current BGP table 
# and analyse the neighbors of the AS area
import time
import MySQLdb as mysql
import socket
import datetime
from dns import resolver 
d1=datetime.datetime.now() #current time
date=str(d1)
d2=d1-datetime.timedelta(days=1) #previous update date
#-datetime.timedelta(days=1))
date_format=date.split()[0]
date=date.replace('-','').split()[0]
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','ipv6websites')
cur=conn.cursor()
cur.execute("select id, url from ipv6sites  ")
list=cur.fetchall()
for item in list :
  error=0
  print item
  try :
     if len(item[1].split('.'))==2 :
       ans=resolver.query('www.'+item[1],'AAAA')
     else :
       ans=resolver.query(item[1],'AAAA')
  except  Exception, err :
    print err
    error=1
  else :
     print ans.rrset[-1]
     cur.execute("update ipv6sites set ipv6addr='%s' where id='%d'" %  (str(ans.rrset[0]).split()[-1], item[0]))
     cur.execute("commit")
  if error==0 :
    continue
  if item[1].strip().find('www')==0 :
    res=item[1].replace('www','ipv6')
  else : 
    res='ipv6.'+item[1]
  try :
       ans=resolver.query(res,'AAAA')
  except  Exception, err :
    print err
    error=1
  else :
     print ans.rrset[-1]
     cur.execute("update ipv6sites set ipv6addr='%s', note='%s' where id='%d'" %  (str(ans.rrset[0]).split()[-1],res, item[0]))
     cur.execute("commit")
cur.close()
conn.close()

