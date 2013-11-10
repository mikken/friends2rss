#!/usr/bin/python3
"""This script generates cookies file to use with LiveJournal.

It will prompt you for username and password, perform a login and
save resulting cookies into a file.

Author: Pavel Volkov
"""

URL = 'https://www.livejournal.com/login.bml?ret=1'

import urllib.request
import urllib.parse
import http.cookiejar
import ssl
import getpass
import sys

values = { 'remember_me' : '1' }
values['user'] = input('Username: ')
values['password'] = getpass.getpass()
jar = http.cookiejar.MozillaCookieJar()
cooker = urllib.request.HTTPCookieProcessor(jar)
https_sslv3_handler = urllib.request.\
        HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv3))
opener = urllib.request.build_opener(cooker, https_sslv3_handler)
data = urllib.parse.urlencode(values).encode('utf-8')
print('opening page...')
try:
    req = urllib.request.Request(URL, data)
except urllib.error.URLError:
    sys.stderr.write("Couldn't get response from server\n")
    sys.exit(1)
response = opener.open(req)
print('saving cookies...')
jar.save('lj_cookies.txt')
respstr = response.read().decode('utf-8')
if len(jar) == 0:
    sys.stderr.write('Did not receive any cookies\n')
    sys.exit(2)
if respstr.find("name='action:logout'") == -1:
    sys.stderr.write('Response does not contain "login flags"\n')
    sys.exit(3)
