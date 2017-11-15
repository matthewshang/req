"""
Prototype skyward access
"""

import configparser
import requests
import lxml.html
import gradebook

config = configparser.ConfigParser()
config.read("config.txt")

username = config.get('configuration', 'username')
password = config.get('configuration', 'password')
region = config.get('configuration', 'region')

BASE_URL = 'https://www01.nwrdc.wa-k12.net/scripts/cgiip.exe/WService={}/'.format(region)
LOGIN = 'skyporthttp.w'
HOME = 'sfhome01.w'
GRADEBOOK = 'sfgradebook001.w'

def login(s):
    data = { 'requestAction': 'eel' }

    params = {
        'method': 'extrainfo',
        'codeType': 'tryLogin',
        'codeValue': username,
        'login': username,
        'password': password
    }

    headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
    return s.post(BASE_URL + LOGIN, data=data, params=params, headers=headers)

def fill_session(split_text):
    session_data = {}
    session_data['dwd'] = split_text[0]
    session_data['web-data-recid'] = split_text[1]
    session_data['wfaacl-recid'] = split_text[2]
    session_data['wfaacl'] = split_text[3]
    session_data['nameid'] = split_text[4]
    session_data['enc'] = split_text[-2]
    session_data['encses'] = split_text[-1]
    return session_data

def login_home(s, session_data):
    data = { 'hCompName': 'ESD189-WEB-06' }
    params = {
        'dwd': session_data['dwd'],
        'wfaacl': session_data['wfaacl'],
        'encses': session_data['encses'],
        'encsec': '',
        'nameid': session_data['nameid'],
        'duserid': username,
        'enc': session_data['enc'],
        'wfaacl-recid': session_data['wfaacl-recid'],
        'web-data-recid': session_data['web-data-recid'],
    }
    return s.post(BASE_URL + HOME, data=data, params=params)

def get_grades(s, session_data):
    data = {
        'sessionid': session_data['sessionid'],
        'encses': session_data['encses']
    }
    params = {
        'sessionid': session_data['sessionid'],
        'encses': session_data['encses']
    }
    return s.post(BASE_URL + GRADEBOOK, data=data, params=params)

with requests.Session() as s:
    r = login(s)
    session_data = fill_session(r.text[4:-5].split("^"))
    print(session_data)
    r = login_home(s, session_data)

    home_html = lxml.html.fromstring(r.text)
    hiddens = home_html.xpath(r'//input[@type="hidden"]')
    for x in hiddens:
        session_data[x.attrib['name']] = x.attrib['value']

    # r = get_grades(s, session_data)
    # print(r.headers)
    # with open("gradebook.html", "w") as file:
    #     file.write(r.text)
        
    with open("gradebook.html", 'r') as f:
        text = f.read()
        gradebook = gradebook.build_gradebook(text)
        entry = gradebook.table[1][1]
        print(entry.attribs)
