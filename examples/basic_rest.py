#!/usr/bin/python

from falcons_nest.response_helpers import JsonResponse, HtmlResponse
from falcons_nest import WsgiHandler

class APP(WsgiHandler):
    def GET(self, req):
        return HtmlResponse("Hello World!!")
        
    def POST(self, req):
        return JsonResponse( {'Hello': 'World'} )
    

if __name__ == '__main__':
    pass
