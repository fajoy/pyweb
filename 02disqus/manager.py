import traceback
import json
from  json import JSONEncoder
import logging
from logging import Handler
import gevent
import os
log = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
ch.setLevel(logging.INFO)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)
log.setLevel(logging.DEBUG)


class LogWebSocketHandler(Handler):
    def __init__(self, ws):
        Handler.__init__(self)
        self.ws = ws

    def emit(self, record):
        msg = self.format(record)
        self.ws.send(msg)

class BaseJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (tuple,list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)

class RpcDispatcher(object):
    def __init__(self, callbacks):
        self.callbacks = callbacks
        super(RpcDispatcher, self).__init__()
    def dispatch(self, method=None, args=[] ,kwargs={}):
        for proxyobj in self.callbacks:
            return getattr(proxyobj, method)(*args,**kwargs)

class WebSocketConsumer(object):
    def __init__(self,manager):
        self.manager=manager
        self.dispatcher=RpcDispatcher([manager ,])
        self.log = logging.getLogger(str(gevent.getcurrent()))

    def recv_loop(self):
        ws=self.manager.ws
        self.log.setLevel(logging.DEBUG)
        ch = LogWebSocketHandler(ws)
        ch.setLevel(logging.WARN)
        ch.setLevel(logging.INFO)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        try:
            while True:
                self.receive()
        finally:
            log.removeHandler(ch)

    def receive(self):
        data = self.manager.ws.receive()
        try:
            jsondict = json.loads(data)
            self.dispatcher.dispatch(**jsondict)

        except Exception as err:
            self.log.exception('WebSocket Recv Data: %s', data)

class WebSocketManager(object):
    def __init__(self,environ,start_response):
        self.environ=environ
        self.ws = environ["wsgi.websocket"]
        WebSocketConsumer(self).recv_loop()

    def rpc(self,js):
        self.ws.send(js)
        
    def lsdir(self):
        id_prefix="pages-"
        walk_path="./pages"
        top_path=os.path.abspath(os.path.join(os.path.dirname(__file__),walk_path ))
        start_path=os.path.abspath(os.path.join(os.path.dirname(__file__),walk_path ))
        items=[]
        for directory,dirnames,filenames in os.walk(top_path):
            dirn=os.path.relpath(directory,start=start_path)
            files = [   {"id": "file-"+os.path.relpath(directory+"/"+filename,start=start_path),
                        "img":"icon-page",
                        "text":filename,}
                        for filename in filenames]
            item={"id":id_prefix+dirn,
                  "text": dirn ,
                  "img": 'icon-folder',
                  "expanded": False,
                  "count":len(files),
                  "nodes":files,
            }
            items.append(item)

        js="""w2ui.sidebar.insert('%s',null,%s);""" % (id_prefix,json.dumps(items))
        self.rpc(js)

    def writefile(self,path,cxt):
        fd = open("pages/"+path,"w")
        fd.write(cxt)
        fd.close()

    def readfile(self,path):
        cxt=open("pages/"+path).read()
        self.rpc("readfile(%s)" %json.dumps(cxt))

    def pyexec(self,code):
        env=locals()
        env["log"] = logging.getLogger(str(gevent.getcurrent()))
        exec """import gevent.monkey
gevent.monkey.patch_all()
""" + code in locals()
