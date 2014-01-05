#!/usr/bin/env python
import os,sys
import traceback
import json
from paste.deploy import loadapp
import gevent
from gevent import pywsgi
from gevent.pool import Pool
from geventwebsocket.handler import WebSocketHandler

from webob import Request,Response  
from HTMLParser import HTMLParser
import logging

log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
ch.setLevel(logging.INFO)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
log.setLevel(logging.DEBUG)

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def escape(text):
    return "".join(html_escape_table.get(c,c) for c in text)

def background(_pool,*args,**kwargs):
    from  pprint import pformat
    while True:
        gevent.sleep(2)
        log.debug("gthread count: %s" %len( _pool))
    return

def websocket_app(environ, start_response):
    from manager import WebSocketManager
    manager=WebSocketManager(environ, start_response)

class ShowHead():
    def __init__(self,*args,**kwargs):
        pass
    def __call__(self,environ,start_response,*args,**kwargs):
        req = Request(environ)
        res = Response()
        res.status = "200 OK"
        res.content_type = "text/plain"
        from pprint import pformat
        res.body =  pformat(req.headers.items(),indent=4)
        return res(environ,start_response)
    @classmethod
    def factory(cls,global_conf,**kwargs):
        return cls()

if __name__ == "__main__":
    configfile="paste.ini"
    appname="main"
    wsgi_app =loadapp("config:%s" % os.path.abspath(configfile), appname)
    
    wsgi_app['/head']=ShowHead.factory(os.path.abspath(configfile))

    wsgi_app['/ws']=(websocket_app)
    
    _pool = Pool(100)
    _pool.spawn(background,_pool)
    server = pywsgi.WSGIServer(("0.0.0.0", 18080)
                ,wsgi_app
                ,handler_class=WebSocketHandler
                ,spawn=_pool
                )

    server.serve_forever()

