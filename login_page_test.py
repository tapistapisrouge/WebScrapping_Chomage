# -*- coding: utf-8 -*-
"""
Created on Mon Sep 13 15:12:47 2021

@author: amaur
"""

import requests

USERNAME = 'amaurypaget@gmail.com' # put correct usename here
PASSWORD = 'A0mau1ry' # put correct password here

LOGINURL = 'https://emploi.apecita.com/front-identifier.html'
DATAURL = 'https://emploi.apecita.com/front-offres.html'

user_agent_amaury = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0' 

session = requests.session()

req_headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': user_agent_amaury
}

formdata = {
    'pseudo': USERNAME,
    'mot_de_passe': PASSWORD
}

# Authenticate
r = session.post(LOGINURL, data=formdata, headers=req_headers, allow_redirects=False)
print(r.headers)
print(r.status_code)
print(r.text)

# Read data
r2 = session.get(DATAURL, headers=req_headers)
print("___________DATA____________")
print(r2.headers)
print(r2.status_code)
print(r2.text)