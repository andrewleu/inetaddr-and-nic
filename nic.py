# download all the number assignment and allocation table from every NIC, and 
# Insert to a table, the internet numbers include AS ipv6 and ipv4 address,
import MySQLdb as mdb        
import os                 
import sys                  
def nicStat(nic): 
  if nic=='ripe-ncc' :
    filename= 'delegated-ripencc-latest'
    os.system('rm -f /root/ipaddr/%s' % filename)
    os.system('wget ftp://ftp.apnic.net/pub/stats/ripe-ncc/%s  -O /root/ipaddr/%s' % (filename,filename)) 
    """ elif nic=='arin' :
    filename='delegated-arin-extended-latest'
    os.system('rm -f /root/ipaddr/%s' % filename)
    os.system('wget --prefer-family=ipv6  ftp://ftp.apnic.net/pub/stats/arin/%s -O /root/ipaddr/%s' % (filename,filename))
    elif nic=='apnic' :
    filename='delegated-apnic-extended-latest'
    os.system('rm -f /root/ipaddr/%s' % filename)
    os.system('wget ftp://ftp.apnic.net/pub/stats/%s/%s  -O /root/ipaddr/%s' % (nic,filename,filename))
    print 'apnic'
    """
  else :
     filename='delegated-'+nic+'-extended-latest'
     os.system('rm -f /root/ipaddr/%s' % filename) ;#rm the file      
     os.system('wget ftp://ftp.apnic.net/pub/stats/%s/%s  -O /root/ipaddr/%s' % (nic,filename,filename))         
  conn=mdb.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')         
  filename='/root/ipaddr/'+filename                  
  fhandler=	file(filename,'r')         
  cnt=0                    
  cur=conn.cursor()                  
  while True :
           error=0
           cnt+=1
  #if cnt % 1000==0 :
  #   print cnt         
           line=fhandler.readline()         
  	#print line.find('*')             
  	#print line[0]                    
  	#sys.stdin.read(1)                
    	#print len(line)                  
           if len(line)==0 :                
  		   break       
           line=line.strip()
           line=line.split('|')
           if len(line[0])<3 :
              continue
#  print line
#  sys.stdin.read(1)  
#  print len(line)           
           if len(line) >=7 :               
# 	 	 		print line                     
 	     if cur.execute("select addr, block from inet_num where addr='%s' and date='%s' " \
             % (line[3],line[5])) ==0 :  #no in the table      
 	 	line=tuple(line)
                print line    
                try :         
 	 	   cur.execute("insert inet_num(NIC,CC,type,addr,block,date,state) value('%s','%s','%s','%s','%s','%s','%s') " % line[0:7]) 
                except mdb.Error, e  :
                   print "Error is %s" % e
                   error=1
                except  :
                   error=1
                if error :         
                   continue
             conn.commit() 
#    else:
#        print 'pass '              
  fhandler.close()
  conn.close()
nicStat('arin')
niclist=['ripe-ncc','arin','afrinic','lacnic'] 
for nic in niclist :     
	nicStat(nic)
            

