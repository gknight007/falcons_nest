#!/usr/bin/python
'''
Created on Aug 26, 2014

@author: gknight
'''

from json import dumps
from falcon.status_codes import HTTP_200
from os.path import getsize


basicExtensions = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.txt': 'text/plain',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png'
}

class ResponseBase:
    def __init__(self, status=HTTP_200 , body=None, headers={}):
        self.status = status
        self.body = body
        self.headers = headers
        self.content_type = 'text/plain'
        
    def formatResponse(self, resp):
        resp.status = self.status
        
        if self.body:
            resp.body = self.body
            
        #Handle redirect case
        if hasattr(self, 'location'):
            resp.location = self.location
        
        resp.content_type = self.content_type

        #Add any custom HTTP headers
        resp.set_headers(self.headers)
        
        
class StreamResponseBase:
    def __init__(self, filePath, status=HTTP_200 , headers={}):
        self.status = status
        self.filePath = filePath
        self.headers = headers
        
    def formatResponse(self, resp):
        resp.status = self.status
        
        resp.stream = open(self.filePath)

        resp.stream_len = getsize(self.filePath)

        resp.content_type = self.content_type
        
        #Add any custom HTTP headers
        resp.set_headers(self.headers)


class JsonResponse(ResponseBase):
    '''
    '''
    def __init__(self, body, status=None, headers={} ):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'application/json'
        self.body = dumps(body)
        self.headers = headers

class RawJsonResponse(ResponseBase):
    '''
    '''
    def __init__(self, body, status=None, headers={} ):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'application/json'
        self.body = body
        self.headers = headers
    
    
class TextResponse(ResponseBase):
    '''
    '''
    def __init__(self, body, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'text/plain'
        self.body = body
    
class TextFileResponse(ResponseBase):
    '''
    '''
    def __init__(self, filePath, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'text/plain'
        
        with  open(filePath) as f:
            self.body = f.read()

    
    
class HtmlResponse(ResponseBase):
    '''
    '''
    def __init__(self, body, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'text/html'
        self.body = body
    

class HtmlFileResponse(ResponseBase):
    '''
    '''
    def __init__(self, filePath, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'text/html'
        with  open(filePath) as f:
            self.body = f.read()

    
class AutoTypeFileResponse(StreamResponseBase):
    def __init__(self, filePath, status=HTTP_200, headers={}):
        StreamResponseBase.__init__(self, filePath, status=status, headers=headers)
        idx = filePath.rfind('.')
        if idx == -1:
            pass #FIXME: handle cant find extension case
        
        ext = filePath[idx:]
        
        if ext in basicExtensions:
            self.content_type = basicExtensions[ext]
        else:
            pass #FIXME: handle cant find extension case
    
class OctetStreamResponse(ResponseBase):
    '''
    '''
    def __init__(self, inData=None, inFile=None, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.content_type = 'application/octet-stream'
        if inData:
            self.stream_len = len(inData)
            self.body = inData
        #resp.stream, resp.stream_len, set_headers(headers)
        
    def formatResponse(self, resp):
        resp.status = self.status
        
        if self.body:
            resp.body = self.body
            
        elif hasattr(self, 'stream'):
            resp.steam = self.stream
        
            
        #Add any custom HTTP headers
        resp.set_headers(self.headers)


class PermRedirectResponse(ResponseBase):
    '''
    '''
    def __init__(self, location, headers={} ):
        ResponseBase.__init__(self, headers=headers)
        self.status = '301 Moved Permanently'
        self.headers['location'] = location

class TempRedirectResponse(ResponseBase):
    '''
    '''
    def __init__(self, location, headers={} ):
        ResponseBase.__init__(self, headers=headers)
        self.status = '307 Temporary Redirect'
        self.headers['location'] = location
    
class InternalErrorResponse(ResponseBase):
    '''
    '''
    def __init__(self, body=None, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.status = '500 Internal Server Error'
        if body:
            self.body = body
    
class UnauthorizedResponse(ResponseBase):
    '''
    '''
    def __init__(self, headers={}):
        ResponseBase.__init__(self, headers=headers)
        self.status = '401 Unauthorized'
    
    
    
    
if __name__ == '__main__':
    pass
