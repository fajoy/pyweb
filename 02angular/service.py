#!/usr/bin/env python
import os,sys
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from paste.deploy import loadserver, loadapp
import logging
log = logging.getLogger()
configfile="paste.ini"
appname="main"
servername="main"

def make_app():
    return loadapp("config:%s" % os.path.abspath(configfile), appname)

def main():
    server = loadserver("config:%s" % os.path.abspath(configfile), servername)
    wsgi_app=make_app()
    server(wsgi_app)
    server.serve_forever()

if __name__=="__main__":
    main()

