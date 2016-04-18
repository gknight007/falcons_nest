#!/usr/bin/python

import requests
import random
import string
import sys
import shlex
import subprocess
import os
from signal import SIGTERM

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
headers = {'x-header1': '1 header', 'x-header2': '2 header'}
postData = {'post-data': '12345'}

testPort = 8080
testUrl = 'http://localhost:%s/reflector/sub_path' % testPort

def setup_func():
  dirPath = os.path.dirname(__FILENAME__)
  cfgPath = os.path.join(dirPath, 'smoke_test.cfg')
  cmd = 'falcons_nest -c %s' % cfgPath

  startDaemonExitStatus = subprocess.call( shlex.split(cmd) )

  assert startDaemonExitStatus == 0, "Failed to start API service for smoke test. We have a big problem!"
  

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



@with_setup(setup_func, teardown_fun)
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
    kwargs.update( {'data': jsonPostData} )

  r = getattr(requests, httpMethod)(testUrl, **kwargs)

  reqDump = dumpRequest(kwargs)

  assert r.status_code == 200, "Failed to get HTTP 200 for %s" % reqDump
  jsonResp = r.json()
  assert jsonResp['method'] == httpMethod, "Wrong HTTP method reflected. Expecting: '%s', Actual: '%s'" % (httpMethod, jsonResp['method'])
  #FIXME: add test to check params and body
  if sendBody: pass 

  for k,v in headers.iteritems():
    assert r.headers.has_key(k), "Missing expected header %s for %s" % (k, reqDump)
    assert r.headers[k] == v, "Header value error header %s for %s" % (k, reqDump)



