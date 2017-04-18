import time
import sys
import MySQLdb as mysql
#update the CC code which is not find by other query

def updateCC(whereabout, as_code) :
  conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
  cur=conn.cursor()
  cur.execute("select id, %s from aspath where %s='-' "  % (as_code,whereabout))
  aslist=cur.fetchall() ;# all the ASes do not have the cc code
  n=0; count=0;
  print aslist;
  while n< len(aslist) :
    items=aslist[n]
    try:
        longas=items[1].split('.')   ;# 32bits as number
        asn=int(longas[0])*65536+int(longas[1])
    except  :
        asn= int(items[1]) ;  #16bits as number
    if cur.execute("select cc, id,  addr, block,date from inet_num where type='asn' and (cast(addr as  unsigned))<='%s'  and (cast(addr as unsigned)+block)>'%s' order by date desc" % (asn, asn)) :
        a=cur.fetchall();
        print a
        cc=a[0] 
        count=count+1
        if  cc[0]!='ZZ' and cc[0]!='' :
          try :
             cur.execute("update aspath set %s ='%s' where id='%s'" %(whereabout,cc[0], items[0]))
          except mysql.Error :
             print mysql.Error
    n=n+1
  conn.commit()
  cur.close()
  conn.close()
  print count

updateCC("orias","asn")
updateCC("desas",'nextasn')

