# -*- coding: utf-8 -*-
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello %s!' % app.config['SITENAME'].title()
