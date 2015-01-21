#this script will download current BGP table and analyse 
#the adjecency of the AS area for ipv4 domain
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
type='ipv4'
filename='/home/ipaddr/bgptable.txt'
args=sys.argv
if len(args) <2 :
    print "-n new check"
    print "-g go on"
    exit()
fhandler=     file(filename,'r')
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
n=0
cur.execute("select nextasn from aspath where type='cnt'")
# asn to store the times for checking of ipv4
cnt=int(cur.fetchone()[0])
if args[1] == '-n' :
    os.system('rm -f %s' % filename) ;#rm the file                                
    os.system('wget http://bgp.potaroo.net/as6447/bgptable.txt  -O %s' % filename)
# asn to store the times for checking of ipv4 
    cnt=cnt+1
    cur.execute("begin")
    cur.execute("update aspath set nextasn = '%s' where type='cnt'" % str(cnt))  
    cur.execute('commit')
    cur.execute("begin")
    cur.execute("update aspath set locked=0 where type='%s'" % type) #unlock all ipv4 entry
    cur.execute("commit")
elif args[1]!='-g' :
    print "-n new check"
    print "-g go on" 
    exit()
cur.execute("select max(locked) from aspath where type='ipv4'")
readlines=int(list(cur.fetchone())[0])
cur.execute("commit")
while True :
   line=fhandler.readline()
   n+=1
   if n %1000 == 0:
      print n  
   if line== '' :
      break
   while line[0]!= '*' : 
     n+=1
     line=fhandler.readline()
   while n < readlines :
     n+=1
     line=fhandler.readline()
   line=line.strip().replace(","," ").replace("{", "").replace("}","")
   line=list(line.split()[6:])

   origin=['6447',] #originate from as 6447
   line=origin+line
   i=0; # print line
   while i < len(line)-2 : #the last one in list is 'i' 'e' or '?'
      if line[i]!=line[i+1] : #the next ASN should be different from the first one
           if cur.execute("select id, connect from aspath where type='%s' and `asn`='%s'and nextasn='%s' and locked=0 " \
            % (type,line[i],line[i+1]))==0 :
              if cur.execute("select id, connect  from aspath where type='%s' and `asn`='%s' \
                and nextasn='%s' " % (type,line[i],line[i+1]))!= 0 :
                  if n%1000 ==0:
                      line=cur.fetchone()
                      cur.execute("commit")
                      cur.execute("update aspath set locked=%s where id=%s" % (n, line[0]))
                  cur.execute("commit") 
                  i+=1; continue      #it is locked, do nothing
            #first insert in the list  
              cur.execute("commit")
              cur.execute("insert aspath(type,`asn`,nextasn) value('%s','%s','%s')" % (type,line[i],line[i+1]))
              cur.execute('commit')
           else : 
             
             fetch=list(cur.fetchone()) ; cur.execute("commit")
             print fetch
             if fetch[1] < cnt :
                 cur.execute("update aspath set connect=connect+1,locked=1 where id=%s" % fetch[0]) 
                 cur.execute('commit')
      i+=1
  
fhandler.close()
'''
cur.execute("select addr from inet_num where type='asn' and CC='CN'")
list=cur.fetchall()
for asn in list :
   cur.execute("begin")
   cur.execute (" update aspath set note='CN' where asn='%s' and note=''" % asn[0])
   print asn[0]
   cur.execute( "commit")
'''
cur.close() 
conn.close()

      
      

   


   

