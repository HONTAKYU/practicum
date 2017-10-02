import requests
import json
import os
import time
import urllib2

jsurl = 'http://54.183.15.129:80'


#SQLi - SELECT, comment after email
session = requests.Session()
auth = json.dumps({'email': 'admin@juice-sh.op\'--', 'password': 'whocares'})
login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
print("SQLi TC1 SELECT, comment after email - response status_code: %d"%(login.status_code))

#SQLi - SELECT, password "or 1=1--"
session = requests.Session()
auth = json.dumps({'email': 'admin@juice-sh.op', 'password': '\' OR 1=1--'})
login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
print("SQLi TC2 SELECT, password or 1=1 -- - response status_code: %d"%(login.status_code))

#SQLi - TC3, UNION SELECT
payload = {'q': 'invalid\')) UNION SELECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--'}
login = requests.get('http://54.183.15.129/#/search',params=payload)
print("SQLi TC3 SELECT, UNION SELECT - response status_code: %d"%(login.status_code))

#SQLi - TC4, WAF Bypass (comment)
payload = {'q': 'invalid\')) UNI/**/ON SEL/**/ECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--'}
login = requests.get('http://54.183.15.129/#/search',params=payload)
print("SQLi TC4 SELECT, UNION SELECT (comment) - response status_code: %d"%(login.status_code))

#SQLi - TC5, WAF Bypass (URL encoding)
payload = {'q': 'invalid\')) U%6eION SE%6cECT NULL,email,password,id,NULL,NULL,NULL,NULL FROM USERS--'}
login = requests.get('http://54.183.15.129/#/search',params=payload)
print("SQLi TC5 SELECT, UNION SELECT (URL encoding) - response status_code: %d"%(login.status_code))


print("")
# Normal - Normal Login TC1
session = requests.Session()
auth = json.dumps({'email': 'admin@juice-sh.op', 'password': 'admin123'})
login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
print("Normal Login TC1, admin login - response status_code: %d"%(login.status_code))

# Normal - Normal Login TC2
session = requests.Session()
auth = json.dumps({'email': 'jeff_tianyu_liu@126.com', 'password': 'qazwsx123'})
login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
print("Normal Login TC2, user login - response status_code: %d"%(login.status_code))

#Normal - Normal Login TC3, with wrong password
session = requests.Session()
auth = json.dumps({'email': 'admin@juice-sh.op', 'password': 'wrongpassword'})
login = session.post('{}/rest/user/login'.format(jsurl),
                     headers={'Content-Type': 'application/json'},
                     data=auth)
print("Normal Login TC3, login with wrong password - response status_code: %d"%(login.status_code))

#Normal - Normal Search TC4
payload = {'q': 'apple'}
login = requests.get('http://54.183.15.129/#/search',params=payload)
print("Normal Search TC4, apple - response status_code: %d"%(login.status_code))

#Normal - Normal Search TC5, with non-existing search results
payload = {'q': 'bananababa'}
login = requests.get('http://54.183.15.129/#/search',params=payload)
print("Normal Search TC5, bananababa - response status_code: %d"%(login.status_code))

