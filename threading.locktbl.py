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
    def readaLine(self):
    	line=self.fhandler.readline()
    	self.n+=1
        #print "processing"+str(self.n)
        #print "from file"+line
        if self.n %100000 == 0:
#          print 'processed lines: '+ str(self.n) 
          nowa=int(time.time())
#          print str(nowa)
          #print line
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
         e=''
         mutex.acquire(2)
         try :
            line=rfile.readaLine()
         except Exception  as e :
            print  "reading line error %s" % e
         finally:
         #print "as path "+str(line)
           n=rfile.n
           mutex.release()
         if e :
             continue
         if line== '' :
            cur.close()
            conn.close()
       	    return 1
         i=0;  #print "as path %s" % line
         #time.sleep(2)
         try:                      
           int(line[len(line)-1])
         except Exception :
           tail=2   ; # if the line ends with i e ?, tail is 2
         else :
           tail=1   ;#or tail is 1
         if n%10000==0 :
            print n 
            print line
         while i < len(line)-tail : #the last one in list is not  'i' 'e' or '?'
             if n%10000==0 :
                  print "as adjecency:"+" "+line[i]+" "+line[i+1]
             if line[i]!=line[i+1] : #the next ASN should be different from the first one
                 #cur.execute("lock table aspath write")
                  try :
                     cur.execute("select id from aspath  where type='%s' and `asn`='%s'and nextasn='%s' for update \
                     "  % (type,line[i],line[i+1]))
                     entry=cur.fetchone()
                     if entry is None or entry[0]=='':
                        cur.execute("insert aspath (type,`asn`,nextasn,`1stins`,locked,up_date) \
                        value('%s','%s','%s',substring(now(),1,10),'%s',substring(now(),1,10))" % (type,line[i],line[i+1],n))
                     else :
                        cur.execute("update aspath set connect=connect+1, up_date=substring(now(),1,10) where id=%d" % entry[0] )   
                  except Exception as e :
                      print entry
                      print "mysql op error %s" % e 
                  finally :
                       cur.execute("commit")
             i=i+1 ;# next  item  in the read line     
global rfile
global mutex
mutex=threading.Lock()
global cnt
global timing
global type
type='ipv4'
filename='bgptable.txt'
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
timing=int(time.time())
lck=line[1]
startTime=timing
#lck=1
"""
cnt=int(line[0])
cur.execute("select max(locked) from aspath  where type='ipv4'")
readLines=int(list(cur.fetchone())[0])
print str(readLines)+' read'+ str(lck)
cur.close()
conn.close()
filename='bgptable.txt'
# asn to store the times for checking of ipv4
if lck==0 :
"""
if 1 :
    #os.system('rm -f %s' % filename) ;#rm the file                         
    print "Downloading"     
    #os.system('wget -q http://bgp.potaroo.net/as6447/bgptable.txt  -O %s' % filename)
# asn to store the times for checking of ipv4 
    #cnt=cnt+1
    #cur.execute("unlock tables")
    #cur.execute("begin")
    #cur.execute("update aspath  set nextasn = '%s', locked=1 where type='cnt'" % str(cnt))  
    #cur.execute('commit')
    #cur.execute("begin")
    #cur.execute("update aspath  set locked=0 where type='%s'" % type) #unlock all ipv4 entry
    #cur.execute("commit")
    readLines=0  
#elif args[1]!='-g' :
#    print "-n new check"
#    print "-g go on" 
#    conn.close();  exit()
    conn.close() 
rfile=FileReading(filename)
if rfile.skiplines(readLines) ==0 :
   del rfile; exit()
for thrd in range(12) :
    try:
	th=updatedb()
	th.start()
    except:
        sleep(3)
#   del rfile
        print "Exception for threading occurs"
    finally:
      time.sleep(1)
      print "OK"
for thrd in range(12) :
  try :
    th.join()
  except e:
    print e
"""
if completed==1 :
   conn=mysql.connect(dbaddr,'ipv6bgp','ipv6','NICstat')
   cur=conn.cursor()
   cur.execute("update aspath  set locked=0 where type='cnt'"); 
   cur.execute("insert entries(type,entries,date) value('%s','%s',now())" % (type,rfile.n)) 
   cur.execute("commit")
   cur.close()
   conn.close() 
"""
endTime=int(time.time())
print "Duration %s"  % (endTime-startTime)
#del rfile
print "Exiting"
exit()

