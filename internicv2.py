#this script will check who owns  specific internet numbers like ipv4 or ipv6 addresses
#and ASN via whois  
import time
import sys
import MySQLdb as mysql
import socket
conn=mysql.connect('127.0.0.1','ipv6bgp','ipv6','NICstat')
cur=conn.cursor()
niclist ={ 'apnic' : ['whois.apnic.net',['netname:','descr:'],['as-name:','descr:','as']],
      'arin' : ['whois.arin.net',['OrgName:','Country:'],['OrgName:','Country:','']],
      'afrinic' : ['whois.afrinic.net',['netname:','descr:'],['as-name:','descr:','as']],
      'lacnic' : ['whois.lacnic.net',['owner:','country:'],['owner:','country:','']],
      'ripencc' : ['whois.ripe.net',['netname:','descr:'],['as-name:','descr:','as']]
     }
q=0
c=0
while True :
    q+=1
    line=cur.execute("select id, NIC, type, addr, date from inet_num where agency ='' or agency='%' order by rand() limit 1")
    if line ==  0:
        break   
    line=cur.fetchone() 
    cur.execute("begin")
    cur.execute("select id, NIC, type, addr, date from inet_num where date='%s' and addr='%s' for update" % (line[4], line[3]))
    if niclist[line[1]] !='' :
        nicname=niclist[line[1]]
    else :
        cur.execute('commit')
        c+=1
        continue
    #print line
    if  line[1]!='afrinic' :
      try:   #try to connect ipv6 first
        socket.setdefaulttimeout(30)   #30 secs to timeout
        sock=socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.connect((nicname[0],43))
      except socket.error:
        try:  #then ipv4
           sock.close()
           sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.connect((nicname[0],43))
        except socket.error :
           sock.close(); print 'socket error... '
           print sys.exc_info()
           cur.execute('commit')
           c+=1
           continue  #all failed
    else :
        try:  #then ipv4
              
           sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           sock.connect((nicname[0],43))
        except socket.error :
           sock.close(); print 'error 1'
           print sys.exc_info()        
           cur.execute('commit')
           c+=1
           continue  #all failed    
    asn=0
    if line[2]== 'asn' :
        query_addr=nicname[2][2]+line[3]  #generate as query with or without 'as' prefix
        asn=1                             #yes asn query
    else :
        query_addr=line[3]
    query_addr=query_addr+'\r\n'
    sock.send(query_addr)
    response=''
    while True :
        try:
            cache =sock.recv(2048)
        except socket.error:
            sock.close()
            print 'error 2'
            print sys.exc_info()
            cur.execute('commit')
            cache=''
            c+=1
            break
        response+=cache
        if cache == '' :
              break
    sock.close()
    if response =='' :
        cur.execute('commit')
        c+=1
        continue  
    from_char=response.find(nicname[1+asn][0])
    response=response[from_char:]       #and 'descr' 
    to_char=response.rfind(nicname[1+asn][1],0,255)
    tail=response[to_char:]
    to_char+=len(tail.splitlines()[0])
    response=response[0:to_char]    
    response=response.replace(nicname[1+asn][0],'')  #replace 'netname:' 'descr:' or something like it 
    response=response.replace(nicname[1+asn][1],'')
    result=''
    for splt in response.splitlines():
         result+=splt.lstrip()+', '
    result=result.rstrip(', ');
    result=result+' --'
    result=result.replace('\'','*')
    result=result.replace('/','%'); result=result.replace('\\',' ')
    if len(result)>512 :
	result=result[0:511] # too long string   
        print len(result); 
        print result 
    #print result
    #print 'q %s, c %s' %(q, c)
    cur.execute("update inet_num set agency='%s' where id='%s'" % (result, line[0]))
    cur.execute("commit")
    c+=1
    time.sleep(2)
cur.close()
conn.close()





