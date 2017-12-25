#!/usr/bin/python python
# -*- coding: utf-8 -*-
"""
__title__ = 'python_2.7 [requests] test url request'
__author__ = 'tx'
__mtime__ = '2017-12-22'
"""

import os
import sys
import pprint
import requests
import time
from requests import Request, Session
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
# sys.path.append("../Common/pylib")
reload(sys)
sys.setdefaultencoding('utf8')


photo_folder = './img2/'

def usage(processName):
    print "Usage: %s URL  Path" % processName
    print "For example:"
    print "     ..."


def get_nowtime(tStamp=1):
    '''tStamp is 1, return now time by timeStamp.'''
    if tStamp == 1:
        timeStamp = time.time()
        return timeStamp
    else:
        time_local  = time.localtime()
        YMD = time.strftime("%Y-%m-%d", time_local)
        return YMD

def GetMsgEx(url, para=None, cookies=None, data=None, filename=None, debug=0):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        'Connection': 'keep-alive'}
    if para:
        for key in para.keys():
            if para[key] is None:
                del para[key]
            else:
                if key == 'User-Agent' and para['User-Agent'] != '':
                    headers['User-Agent'] = para['User-Agent']
                else:
                    headers[key] = para[key]
    if cookies and len(cookies) != 0:
        headers['cookie'] = cookies

    try:
        if not data or len(data) == 0:
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, data=data)
    except Exception as e:
        # raise e
        print e
        return None
    if str(response.status_code)[0] != '2':
        print "HTTP error, status_code is %s,  url=%s"%(response.status_code, url)
        return None

    if debug:
        print url
        print response.status_code
        pprint.pprint(headers)

    if filename:
        with open(filename, 'wb') as fd:
            for response_data in response.iter_content(1024):
                fd.write(response_data)
        return filename
    else:
        return response.text



def test_urlRequest():
    url = 'https://securityintelligence.com/wp-admin/admin-ajax.php'
    data = {'action': u'ajax_load_more', 'count': u'8', 'catid': u'97', 'offset': '8'}


    response = GetMsgEx(url.strip(), data = data)
    if not response:
        print "request blog_url[%s] faild!" % blog_url
        return None
    print response



if __name__ == "__main__":

    test_urlRequest()