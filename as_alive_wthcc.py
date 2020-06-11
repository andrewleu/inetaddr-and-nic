import time
import sys
import MySQLdb as mysql
#update the CC code which is not find by other query
global conn, cur

def update( as_cc, as_type) :
  try :
     if  cur.execute("select  count(cc)  from as_cc_2days  where cc='%s' and type ='%s' "\
     % (as_cc, as_type)) :
        counter=cur.fetchone()[0]
        cur.execute( "insert into as_alive_wthcc  (`cc`,`type`,`num`,`date`) \
        values ('%s','%s',%d , (select substring(now(),1,10)))" \
        % (as_cc, as_type,counter))
  except Exception as e :
     print 'Errors in func: %s' % e 

if 1 :
     conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
     cur=conn.cursor()
try :
   cur.execute("select distinct cc from as_cc_2days" ) 
   cc_list = cur.fetchall()
   for cc in cc_list :
      if cc[0] :
          update(cc[0],'ipv6')
except Exception as e  :
     print e
finally   :
    cur.execute("commit")
    cur.close()
    conn.close()
