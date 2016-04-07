from falcons_nest.response_helpers import HtmlResponse
from falcons_nest import WsgiHandler

class APP(WsgiHandler):
    def GET(self, req):
        return HtmlResponse("Hello World!", headers={'x-token': 'super secret here'})
        

if __name__ == '__main__':
    pass
