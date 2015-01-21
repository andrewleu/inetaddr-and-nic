package require mysqltcl
global mysqlstatus
set port {3306}
set host {127.0.0.1}
set user {ipv6bgp}
set password {ipv6}
set dbname {NICstat} ;# calculated data
set mysql_handler [mysqlconnect -host $host -port $port -user $user -password $password]
mysqlexec $mysql_handler "set names 'utf8'"
mysqluse $mysql_handler $dbname
while True {
  set result [mysqlsel $mysql_handler "select id, asn from asp where cc='' or cc is NULL order by rand() limit 1 " -list]
  if {$result == ""} {
    break};
  set asn [lindex $result 0 1]
  set cc [mysqlsel $mysql_handler "select cc from inet_num where addr<=$asn and (addr+block-1)>=$asn
  and type='asn' limit 1 " -list]; #puts $cc
  if {$cc ==""} {
    set cc "-" } 
  set error [catch {mysqlexec $mysql_handler "update asp set cc='$cc' where id=[lindex $result 0 0]"} msg]
  if {$error } {
   puts $msg;puts $cc;put $result
   }
}
mysqlclose $mysql_handler 
