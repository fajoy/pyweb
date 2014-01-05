import traceback
import json
from  json import JSONEncoder
import logging
from logging import Handler
import gevent

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
            if not hasattr(proxyobj, method):
                continue
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
                jsondict=self.receive()
                if jsondict:
                    self.dispatcher.dispatch(**jsondict)
        finally:
            log.removeHandler(ch)

    def receive(self):
        data = self.manager.ws.receive()
        try:
            jsondict = json.loads(data)
            return jsondict
        except Exception as err:
            self.log.exception('WebSocket Recv Data: %s', data)

class WebSocketManager(object):
    def __init__(self,environ,start_response):
        self.environ=environ
        self.ws = environ["wsgi.websocket"]
        WebSocketConsumer(self).recv_loop()
    def pyexec(self,code=""):
        env=locals()
        env["log"] = logging.getLogger(str(gevent.getcurrent()))
        exec """import gevent.monkey
gevent.monkey.patch_all()
""" + code in locals()
