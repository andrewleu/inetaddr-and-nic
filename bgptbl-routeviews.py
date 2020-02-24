#to download a full ipv6 bgp table, and convert the table to unique entries
import time
import sys
import MySQLdb as mysql
import socket
import select
import os
import datetime
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
date=str(datetime.datetime.now())
#-datetime.timedelta(days=1))
date_format=date.split()[0]
date=date.replace('-','').split()[0]
"""
filename='rib'+'.'+date+'.'+'0200.bz2'
g_entries=0; c_entries=0 #global entries and china entries
print "Proceeding the BGP table of IPv6"
os.system('rm -f rib*' ) ;#rm the file
print "Downloading"
os.system('wget -q ftp://archive.routeviews.org/bgpdata/%s/RIBS/%s -O rib.bz2' % (date[0:4]+'.'+date[4:6],filename))
os.system('bzip2 -d rib.bz2')
os.system('bgpdump -t dump rib >rib.dump')
dumpfile='./bgptbl/'+'bgp'+date
cnroute='./bgptbl/'+'cnbgp'+date
os.system("sed -n  -e '/^PREFIX.\+/w %s' -e '/^ASPATH.\+/w %s' rib.dump" % (dumpfile,dumpfile))
"""
dumpfile='./bgptbl/'+'bgpv6'+date
cnroute='./bgptbl/'+'cnbgp'+date
if not os.path.isfile(dumpfile) :
   os.system('wget -q http://bgp.potaroo.net/v6/as6447/bgptable.txt -O %s' % dumpfile)
fhandler=  file(dumpfile,'r')
cnaspath= file(cnroute,'w')
error=0; totalLines=0;cnentries=0;cnblocks=0;prvsline='';globalentries=0;
try : 
   err=0 
   if cur.execute("select asn,'' from as_plus_cc where cc='cn'") :
          cnlist=cur.fetchall()
   else  :
        cnlist=''
        print  'cn list is empty'     
   readline=fhandler.readline()
   
   while cnlist :
     line=readline # read PREFIX
     if line=='' :
         break
     line=line.strip()
     blocks=line.split()
     if blocks[0]=='::/0' :
        readline=fhandler.readline()
        continue  #default route
     while True :
       readline=fhandler.readline()
       if readline=='' :
              break 
       if readline.split()[0]!=blocks[0] :  #pass all the same route entries followed
           break    
     asn=blocks[1:]
     globalentries+=1
     try :
        asn=asn[-1] #last as of the aspath
     except Exception, e:
        print e;
        error=1
     if error :
        error=0 
        continue
     if asn.find('{')!= -1 :
        continue
     asn=asn.split('.') ;#16 or 32 bits asn
     if len(asn)==2 :
       asn=int(asn[0])*65536+int(asn[1])
     else :
        asn=int(asn[0])
     asn=[str(asn),'']
     asn=tuple(asn); # print asn
     if asn in cnlist :
       cnentries+=1
       blocks=blocks[0].split('/');
     #  if cnentries%1000==0 : 
       if 1 :
            print "%s: %s" % (cnentries, line)
       cnaspath.write(line+'\n')
    #print outline
       cnblocks+=int(2**(48-int(blocks[1])))
except Exception, e :
   print e
   print line+'\n' +readline 
   err=1
finally :
    fhandler.close()
    cnaspath.write("BGP entries from China: "+str(cnentries))
    cnaspath.close()

try :
  if err!=1 :
    cur.execute("select sum(power(2,(48-block))) from inet_num where  cc='CN' and type='ipv6'") ;
    g_blocks=cur.fetchone()
    cur.execute("insert bgpitems(date,chinabgpitem,totalbgpitem,ratio,type) values('%s','%s','%s','%s','t')" \
    % (date_format,cnentries,globalentries ,float(cnentries)/globalentries))
    cur.execute("insert publish(date,publish, sum,ratio) values('%s', '%s','%s','%s')" \
    % (date_format,cnblocks,g_blocks[0],float(cnblocks)/g_blocks[0]))
except Exception, e :
   print e
cur.execute("commit")
cur.close()
conn.close()
"""
the DB table
CREATE TABLE `bgpitems` (
  `Id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `Date` varchar(20) NOT NULL DEFAULT '',
  `ChinaBgpItem` mediumint(9) unsigned DEFAULT NULL,
  `TotalBgpItem` int(11) unsigned DEFAULT NULL,
  `Ratio` float(8,5) unsigned DEFAULT NULL,
  `type` char(1) DEFAULT '',
  PRIMARY KEY (`Id`,`Date`),
  UNIQUE KEY `id` (`Id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""
