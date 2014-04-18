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

import time
import gevent.monkey
gevent.monkey.patch_all()

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
    while True:
        log.debug("gthread count: %s" %len( _pool))
        time.sleep(1)

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




import base64
import hashlib
import hmac
import simplejson
import time

DISQUS_SECRET_KEY = '9LG7uU4haIt0Ih1DignIdQhphJQW6z1eQp7D0PrDfwJgD0nkXqSBhwJlLskK5cqZ'
DISQUS_PUBLIC_KEY = 't120z4tcfC2bNBzWDXOciIt8HxNg99nuH43kYxcHNmojo2XZtvCCWusO8HN2MX8b'

def get_disqus_sso(user):
    # create a JSON packet of our data attributes
    data = simplejson.dumps({
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
    })
    # encode the data to base64
    message = base64.b64encode(data)
    # generate a timestamp for signing the message
    timestamp = int(time.time())
    # generate our hmac signature
    sig = hmac.HMAC(DISQUS_SECRET_KEY, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()

# return a script tag to insert the sso message
    return """
    (function() {
            var dt = document.createElement('div'); dt.id = 'disqus_thread'; 
            (document.getElementsByTagName('body')[0]).appendChild(dt);
        })();


    var disqus_config = function() {
        this.page.remote_auth_s3 = "%(message)s %(sig)s %(timestamp)s";
        this.page.api_key = "%(pub_key)s";
    }

  var disqus_identifier = 'index'; //a unique identifier for each page where Disqus is present
  var disqus_title = 'cyfang test';// a unique title for each page where Disqus is present
  //var disqus_url = '' a unique URL for each page where Disqus is present';

  var disqus_shortname = 'wuminfajoy'; // required: replace example with your forum shortname

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();


    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function () {
        var s = document.createElement('script'); s.async = true; s.type = 'text/javascript';
        s.src = '//' + disqus_shortname + '.disqus.com/count.js';
        (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
    }());

    """ % dict(
        message=message,
        timestamp=timestamp,
        sig=sig,
        pub_key=DISQUS_PUBLIC_KEY,
    )

class Disqus_Js():
    def __init__(self,*args,**kwargs):
        pass
    def __call__(self,environ,start_response,*args,**kwargs):
        req = Request(environ)
        res = Response()
        res.status = "200 OK"
        res.content_type = "text/javascript"
        user={"id":"cyfang","username":"cyfang","email":"cyfang@cs.nctu.edu.tw"}
        res.body =  get_disqus_sso(user)
        return res(environ,start_response)
    @classmethod
    def factory(cls,global_conf,**kwargs):
        return cls()



if __name__ == "__main__":
    configfile="paste.ini"
    appname="main"
    wsgi_app =loadapp("config:%s" % os.path.abspath(configfile), appname)
    
    wsgi_app['/head']=ShowHead.factory(os.path.abspath(configfile))
    wsgi_app['/disqus.js']=Disqus_Js.factory(os.path.abspath(configfile))

    wsgi_app['/ws']=(websocket_app)
    _pool = Pool(100)
    _pool.spawn(background,_pool)
    server = pywsgi.WSGIServer(("0.0.0.0", 18080)
                ,wsgi_app
                ,handler_class=WebSocketHandler
                ,spawn=_pool
                )

    server.serve_forever()

