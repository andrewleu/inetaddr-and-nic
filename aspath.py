#this script will download the current BGP table of ipv6
# and analyse the neighbors of the AS area
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
type='ipv6'
filename='/home/ipaddr/bgptablev6.txt'
no=0; #lines number
cur.execute("select asn, locked from aspath where type='cnt'")
# asn to store the times for checking ipv6 aspath
ftch=cur.fetchone()
cnt=int(ftch[0])
print "Proceeding the BGP table of IPv6"
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
fhandler=     file(filename,'r')

while True :
   line=fhandler.readline()
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
 #  if no%10000==0 :
 #     print str(no)+' '+str(line)
 #  origin=['6447'] #first ASN should be 6447
 #  line=origin+line
   i=0
   #print str(no)+' '+str(line)
   while i < len(line)- 1:
        #if no%10000==0 :
        #   print line[i]+":"+line[i+1]
        if line[i] != line[i+1] : # asn=asn 
          cur.execute('begin')    
          if cur.execute("select id, connect  from aspath where type='%s' and `asn`='%s' \
           and nextasn='%s' and locked=0 " % (type,line[i],line[i+1]))== 0 :
             if cur.execute("select id, connect  from aspath where type='%s' and `asn`='%s' \
               and nextasn='%s' " % (type,line[i],line[i+1]))!= 0 :
                 i+=1; cur.execute("commit"); continue      #it is locked, do nothing
             
             #print  "as %s to %s" %(line[i],line[i+1])             
             cur.execute("insert aspath(type,asn, nextasn) value('%s','%s','%s') " % (type,line[i],line[i+1]))
             cur.execute('commit')   #first time in BGP path, the entry is locked by default
          else :
             fetch=list(cur.fetchone())
             # print fetch; print no
             if fetch[1] < cnt :
                 cur.execute("update aspath set connect=connect+1, locked=1 where id='%s'" % fetch[0])
                 #lock the row 
                 cur.execute('commit')
        i+=1
fhandler.close()
#this version will test if the connection is stable,and the region 
while True :  #to check the regions for both ends of the aspath
  if cur.execute("select id,asn,nextasn from aspath where note=''  order by rand() limit 1") !=0 :
     line=list(cur.fetchone()); linebkup=line
     if line[1].find('.')>0 : #long ASN some noted as 3.9
        line[1]= str( int(line[1].split('.')[0])*65536+int(line[1].split('.')[1]))
     if cur.execute("select CC from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s" % (line[1],line[1])) ==0 :
        fromAS=('',) #not in the list, pass it
     else: 
        fromAS=cur.fetchone() 
     if line[2].find('.')>0 :
        line[2]= str( int(line[2].split('.')[0])*65536+int(line[2].split('.')[1]))
     if cur.execute("select CC from inet_num where type='asn' and addr<=%s and addr+block-1 >=%s" % (line[2],line[2]))==0 :
        toAS=('',)
     else :
         toAS=cur.fetchone();  #print '%s, %s' %(line[1],line[2])
     note=list(fromAS)[0]+'-'+list(toAS)[0]; #print note 
     cur.execute("begin")
     cur.execute("update aspath set note= '%s' where id='%s' " % (note,line[0]))
     cur.execute( "commit")    
  else :
     break  #end
print "updating database "+str(no)
cur.execute("update aspath set locked=0 where type='cnt'")  
cur.execute("insert entries(type,entries,date) value('%s','%s',now())" % (type,no))
cur.execute("commit")
#unlock the table
cur.close()
conn.close()
      

   


