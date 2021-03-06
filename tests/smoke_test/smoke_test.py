#!/usr/bin/python

import requests
import random
import string
import sys
import shlex
import subprocess
import os
import json
from signal import SIGTERM
from nose.tools import with_setup
from time import sleep

testPlan = '''
1. Start server
	a. directory loader
	b. default configs
	c. json reflector obj
	d. static file mapping
2. Make all basic request types
	a. assert proper reflection
3. Stop server
'''


body='TEST Body'
headers = {'X-HEADER1': '1 header', 'X-HEADER2': '2 header'}
postData = {'post-data': '12345'}

testPort = 8080
testUrl = 'http://localhost:%s/reflector' % testPort

def setup_func():
  dirPath = os.path.dirname(__file__)
  cfgPath = os.path.join(dirPath, 'smoke_test.cfg')
  sys.stdout.write("STARTING DAEMON FOR SMOKE TEST\n")
  cmd = 'falcons_nest --config %s' % cfgPath

  startDaemonExitStatus = subprocess.call( shlex.split(cmd) )

  assert startDaemonExitStatus == 0, "Failed to start API service for smoke test. We have a big problem!"
  sleep(2)

  

def teardown_func():
  pid = open('/tmp/falcons_nest.pid').read()
  try:
    int(pid)
  except:
    sys.stderr.write("WARNING: pidfile /tmp/falcons_nest.pid does NOT contain INT\n")
    return

  try:
    os.kill(pid,0)
  except OSError:
    sys.stderr.write('WARNING: pid in /tmp/falcons_nest.pid was NOT RUNNING\n')
    return 

  os.kill(pid, SIGTERM)



@with_setup(setup_func, teardown_func)
def smoke_test():
  testSet = {
    'get': False,
    'post': True,
    'put': True,
    'delete': False,
    'head': False,
    'options': False,
  }

  for httpMethod, shouldSendBody in testSet.iteritems():
    yield check_base_requests, httpMethod, shouldSendBody


def dumpRequest(kwargs):
  #FIXME:
  sys.stderr.write('')


def check_base_requests(httpMethod, sendBody):
  jsonPostData = json.dumps(postData)
  kwargs = {
    'headers': headers,
  }

  if sendBody:
    r = getattr(requests, httpMethod)(testUrl, headers=headers, data=jsonPostData)
  else:
    r = getattr(requests, httpMethod)(testUrl, headers=headers)


  reqDump = dumpRequest(kwargs)

  assert r.status_code == 200, "Failed to get HTTP 200 for %s" % reqDump
  jsonResp = r.json()
  assert jsonResp['method'] == httpMethod.upper(), "Wrong HTTP method reflected. Expecting: '%s', Actual: '%s'" % (httpMethod, jsonResp['method'])


  #FIXME: add test to check params and body
  if sendBody: pass 

  for k,v in headers.iteritems():
    assert jsonResp['headers'].has_key(k), "Missing expected header %s for %s" % (k, reqDump)
    assert jsonResp['headers'][k] == v, "Header value error header %s for %s" % (k, reqDump)



