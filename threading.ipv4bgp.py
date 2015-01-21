#analyse BGP table of ipv4
#with threading 
import threading
import threading
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
class FileReading :	  
    fhandler=''
    n=0
    def __init__ (self, filename) :
        self.fhandler= file(filename,'r')
        print 'initiating'
        print self.n
	  	
    def __del__ (self):
        self.fhandler.close()
    def skiplines(self,readLines) :
        #while self.fhandler.readline()[0]!='*' :
        #    self.n+=1
      	if readLines != 0 :
           while self.n < readLines :
  		     line=self.fhandler.readline()
  		     self.n+=1
        else :
           line=self.fhandler.readline()
           self.n+=1
        if line== '' :
                 return 0
        print 'startline', self.n
        return 1
    def readaLine(self,timing):
    	line=self.fhandler.readline()
    	self.n+=1
        #print "processing"+str(self.n)
        #print "from file"+line
        if self.n %100000 == 0:
          print 'processed lines'+ str(self.n) 
          nowa=int(time.time())
          nowa=nowa-timing
          print 'duration '+str(nowa)
          pass 
        if line == '' :
           return 0
        line=line.strip().replace(">"," ").replace(","," ").replace("{", "").replace("}","")
        line=line.split()
        line=line[2:]
        return line
    # 
class updatedb (threading.Thread):
    def run(self) :
       conn=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat')
       cur=conn.cursor()
       time.sleep(3)
       print self.name
       while True :
         mutex.acquire(2)
         timing=int(time.time())
         line=rfile.readaLine(timing)
         #print "as path "+str(line)
         n=rfile.n
         mutex.release()
         if line== 0 :
            cur.close()
            conn.close()
       	    return 1
         i=0; # print line
         #time.sleep(2)
         while i <= len(line)-2 : #the last one in list is not  'i' 'e' or '?'
             if line[i]!=line[i+1] : #the next ASN should be different from the first one
                 cur.execute("lock table aspath write")
                 if cur.execute("select id, connect, locked from aspath  where type='%s' and `asn`='%s'and nextasn='%s' \
                  and locked=0 for update "  % (type,line[i],line[i+1]))==0 : #locked or new entry
                    if cur.execute("select id, connect, locked from aspath  where type='%s' and `asn`='%s'and nextasn='%s' \
                    for update "  % (type,line[i],line[i+1]))!=0 : #locked 
                       if n%1000 ==0 and i==0:
                          cur.execute("update aspath  set locked=%s  where type='%s' and `asn`='%s'and nextasn='%s'" \
                             % (n,type,line[i],line[i+1]))
                          #print line[i]+' '+line[i+1];
                       i+=1;cur.execute("unlock tables");  continue      #it is locked, do nothing
                    #new entry, first insert in the list 
                    cur.execute("insert aspath (type,`asn`,nextasn) value('%s','%s','%s')" % (type,line[i],line[i+1]))
                    #print 'new entry'+ line[i]+' '+line[i+1]
                    #time.sleep(1)
                    
                 else :    
                     fetch=list(cur.fetchone()) ; 
                     #print fetch
	             #print self.name
                     #print line
                     if fetch[1] < cnt : # will update the counter just once
                       cur.execute("update aspath  set connect=connect+1,locked=1  where \
                          type='%s' and `asn`='%s'and nextasn='%s'" \
                             % (type,line[i],line[i+1]))
                       #cur.execute("select * from aspath  where id=%s" % fetch[0])
                       #print cur.fetchone();print 'unlocked'
                 cur.execute("unlock tables")
             i+=1	 
global rfile
global mutex
mutex=threading.Lock()
global cnt
global type
type='ipv4'
filename='/home/ipaddr/bgptable.txt'
args=sys.argv
dbaddr="127.0.0.1"
#if len(args) <2 :
#    print "-n new check"
#    print "-g go on"
#    exit()
conn=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
cur.execute("select nextasn,locked  from aspath  where type='cnt'")
line=cur.fetchone()
lck=line[1]
#lck=1
timing=int(time.time())
cnt=int(line[0])
cur.execute("commit")
cur.execute("select max(locked) from aspath  where type='ipv4'")
readLines=int(list(cur.fetchone())[0])
cur.execute("commit")
print str(readLines)+' read'+ str(lck)
cur.close()
conn.close()
# asn to store the times for checking of ipv4
if lck==0 :
    os.system('rm -f %s' % filename) ;#rm the file                         
    print "Downloading"     
    os.system('wget -q http://bgp.potaroo.net/as6447/bgptable.txt  -O %s' % filename)
# asn to store the times for checking of ipv4 
    cnt=cnt+1
    conn=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat')
    cur=conn.cursor()
    cur.execute("begin")
    cur.execute("update aspath  set nextasn = '%s', locked=1 where type='cnt'" % str(cnt))  
    cur.execute('commit')
    cur.execute("begin")
    cur.execute("update aspath  set locked=0 where type='%s'" % type) #unlock all ipv4 entry
    cur.execute("commit")
    readLines=0  
#elif args[1]!='-g' :
#    print "-n new check"
#    print "-g go on" 
#    conn.close();  exit()
    conn.close()    
rfile=FileReading(filename)
if rfile.skiplines(readLines) ==0 :
   del rfile; exit()
startTime=int(time.time())
try:
  for thrd in range(6) :
	th=updatedb()
	th.start()
except:
   th.join()
   sleep(30)
#   del rfile
   print "Exception occurs"
finally:
   th.join()
   time.sleep(60)
   conn=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat')
   cur=conn.cursor()
   cur.execute("update aspath  set locked=0 where type='cnt'"); cur.execute("commit")
   print ("unlock the table for next update")
   cur.close()
   endTime=int(time.time())
   print "Duration %s"  % (endTime-startTime)
   conn.close()
   del rfile

