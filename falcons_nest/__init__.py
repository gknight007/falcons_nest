#!/usr/bin/python


from falcon import API as Falcon_API
from falcon import DEFAULT_MEDIA_TYPE
from falcons_nest.response_helpers import AutoTypeFileResponse


class WsgiHandler(object):
    def dispatchReq(self, req, resp, requestHandlerName):
        '''
        Request dispatcher.  Take our request from 
        falcon and send it to the sub-classed handler.
        We expect a return of an object with a attribute
        named 'formatResponse' that is callable and use it 
        to format the falcon response object, else treat the
        return as the falcon response object.
        '''
        if hasattr(self, requestHandlerName):
            requestHandler = getattr(self, requestHandlerName)
            
            if callable(requestHandler): 
                handlerResponse = requestHandler(req)
                
                if hasattr(handlerResponse, 'formatResponse'):
                    handlerResponse.formatResponse(resp)
                    
                else:
                    resp = handlerResponse
            
    def on_get(self, req, resp):
        '''
        Hook to GET handler for falcon
        '''
        self.dispatchReq(req, resp, 'GET')
        
    def on_post(self, req, resp):
        '''
        Hook to POST handler for falcon
        '''
        self.dispatchReq(req, resp, 'POST')
        
    def on_put(self, req, resp):
        '''
        Hook to PUT handler for falcon
        '''
        self.dispatchReq(req, resp, 'PUT')
    
    def on_update(self, req, resp):
        '''
        Hook to UPDATE handler for falcon
        '''
        self.dispatchReq(req, resp, 'UPDATE')
        
    def on_delete(self, req, resp):
        '''
        Hook to DELETE handler for falcon
        '''
        self.dispatchReq(req, resp, 'DELETE')

    def on_head(self, req, resp):
        '''
        Hook to HEAD handler for falcon
        '''
        self.dispatchReq(req, resp, 'HEAD')
        
        
    def on_options(self, req, resp):
        '''
        Hook to OPTIONS handler for falcon
        '''
        self.dispatchReq(req, resp, 'OPTIONS')
        



class API(Falcon_API):
    __slots__ = ('_after', '_before', '_error_handlers', '_media_type',
                 '_routes', '_default_route', '_sinks', '_logger')
    
    def __init__(self, media_type=DEFAULT_MEDIA_TYPE, before=None, after=None, logger=None):
        Falcon_API.__init__(self, media_type, before=before, after=after)
        
        if logger: #FIXME: add check to see if subclass() of logger.*some_logger*
            self._logger = logger

            #Alias falcon.API logger functions to use self._logger
    def critical(self, msg): self._logger.critical(msg)
    def error(self, msg):    self._logger.error(msg)
    def warn(self, msg):     self._logger.warn(msg)
    def info(self, msg):     self._logger.info(msg)
    def debug(self, msg):    self._logger.debug(msg)


class FalconsNestStaticDirHandler(WsgiHandler):
    def __init__(self, dirRoot):
        self.root = dirRoot
    def on_get(self, req, resp, fileName):
        '''
        Hook to GET handler for falcon
        '''
        AutoTypeFileResponse( join(self.root, fileName) ).formatResponse(resp)




