#correct wrong cc code of the ASes both origination and destination
import time
import sys
import MySQLdb as mysql
def updateCC( as_code, c_code) :
  conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
  cur=conn.cursor()
  n=213681
  while n :
     if cur.execute("select %s, %s from aspath where id=%s for update" % (as_code,c_code,n)) :
       items=cur.fetchone();
       try:
         longas=items[0].split('.')   ;# 32bits as number
         asn=int(longas[0])*65536+int(longas[1])
       except  :
         asn= int(items[0]) ;  
        #16bits as number
       #print asn,n
       if cur.execute("select cc, id,  addr, block,date from inet_num where type='asn' and (cast(addr as  unsigned))<='%s' \
       and (cast(addr as unsigned)+block)>'%s' order by date desc" % (asn, asn)) :
         a=cur.fetchall(); #print a
         cc=a[0] ; #print cc
         if  cc[0]!= items[1] and cc[0]!='ZZ' and cc[0]!='' :
           print n, cc[0], items[1]
           try :
             cur.execute("update aspath set desas ='%s' where id='%s'" %(cc[0], n))
           except mysql.Error :
             print mysql.Error
     n=n-1
     if n%2000==1 :
        conn.commit() 
  conn.commit()
  cur.close()
  conn.close()

#updateCC('asn', 'orias')
updateCC('nextasn','desas')
#desas
#209495 CZ IL
#1L
#209494 CZ IL
#1L
#209488 DE AT
#1L
#209487 DE CH
#1L
#209486 DE CH
#1L
#209460 AE US
#1L
#209459 NO SE
