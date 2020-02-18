import time
import sys
import MySQLdb as mysql
#update the CC code which is not find by other query

def updateCC(whereabout, as_code) :
  conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
  cur=conn.cursor()
  cur.execute("select  distinct now(), %s from aspath where %s='-' or %s ='' or %s is NULL "  % (as_code,whereabout, whereabout, whereabout))
  aslist=cur.fetchall() ;# all the ASes do not have the cc code
  n=0; count=0;
  print "%s has %s items for updating" % (whereabout, len(aslist)) ;
  for items in aslist :
    items=aslist[n];
    if items[1]=='' :
       n+=1
       continue
    if items[1].find('/')!=-1 or items[1].find(":")!=-1 :
          n+=1
          continue
    try:
        longas=items[1].split('.')   ;# 32bits as number
        asn=int(longas[0])*65536+int(longas[1])
    except  :
        asn= int(items[1]) ;  #16bits as number
    if cur.execute("select cc, id,  addr, block,date from inet_num where type='asn' and (cast(addr as  unsigned))<='%s'  and (cast(addr as unsigned)+block)>'%s' order by date desc" % (asn, asn)) :
        a=cur.fetchall();
        #if  n%1000==0 :
        if asn>50000 :
          print "items: "+items[1]
          print a
        cc=a[0] 
        count=count+1
        if   cc[0]!='' :
          try :
           #  cur.execute("update aspath set %s ='%s' where id='%s'" %(whereabout,cc[0], items[0]))
             cur.execute("update aspath set %s='%s' where %s='%s'" % ( whereabout,cc[0],as_code,items[1]))   
          except Exception as e :
             print e
          finally :
             cur.execute("commit")
    n=n+1
  cur.close()
  conn.close()
  print count

updateCC("orias","asn")
updateCC("desas",'nextasn')

