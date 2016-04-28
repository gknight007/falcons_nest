#!/usr/bin/python

from falcons_nest.response_helpers import JsonResponse
from falcons_nest import WsgiHandler

import random, string, sys


class APP(WsgiHandler):
  def reflectAll(self, req, responseData, includeStream=False):
    responseData['params'] = req.params
    responseData['headers'] = req.headers
    if includeStream:
      responseData['data'] = req.stream.read()

    return responseData

  def GET(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData) )

  def POST(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData, includeStream=True) )

  def PUT(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData, includeStream=True) )

  def DELETE(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData) )

  def HEAD(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData) )

  def OPTIONS(self, req):
    responseData = {}
    responseData['method'] = sys._getframe().f_code.co_name
    return JsonResponse( self.reflectAll(req, responseData) )

