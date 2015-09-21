#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from urllib.parse import urlsplit, parse_qsl
from datetime import datetime
from time import time
from jinja2 import Environment, PackageLoader
from glob import glob 
from itertools import chain
from ast import literal_eval
import csv
import json

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        o = urlsplit(self.path)

        if o.path == '/favicon.ico':
            self.send_error(404)
            return 

        q = dict(parse_qsl(o.query))
        self._set_headers()

        if o.path == '/' and 'l' not in q:
            self.output(index())
        
        user = o.path.split('/', 2)[1]

        if 'l' in q:
            writestream(self.address_string(), q['l'])
            
            self.output(show(q['l'].split(maxsplit=1)[0]))

    def do_HEAD(self):
        self._set_headers()
        
    def do_POST(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>content</h1></body></html>")

    def output(self, c):
        return self.wfile.write(bytes(c, 'utf-8'))

def index():
    template = env.get_template('index.html')
    return template.render()

def readevent(e):
    """ returns sid, ip, msts, arg """
    return e

def readfromlogfiles(p):
    streampath = '/'.join([p, '*'])
    files = glob(streampath)
    contents = []   
    for f in files:
        with open(f, 'r', encoding = 'utf-8') as infile:
            for row in csv.reader(infile, delimiter='\t', quotechar='"'):
                contents.append([conv(r) for r in row])
    return contents

def conv(i):
    try:
        return(int(i))
    except:
        try:
            return(literal_eval(i))
        except:
            return(i)

def show(u):
    template = env.get_template('user.html')
    c = readfromlogfiles(logdir)
    contents = [e for e in c if e[2][0].split(maxsplit=1)[0] == u]
    
    return template.render(contents = contents)

def get_millis():
    return int(round(time() * 1000))

def storageformat(ip, m):
    return (sourceid, get_millis(), [m, ip])


def writestream(ip, m):
    fn = datetime.now().strftime('%Y-%m-%d_%H.log')
    fpath = '/'.join([logdir, fn])
    try:
        with open(fpath, "a", encoding='utf-8') as myfile:
            writer = csv.writer(myfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(storageformat(ip, m))
        #    myfile.write(storageformat(ip, m))
    except:
        print("Couldn't write %s to %s" % (m, fn), file=sys.stderr)
    return '' 

def run(server_class=HTTPServer, handler_class=S, port=80):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting server')
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv
    logdir = 'stream'
    sourceid = 0
    env = Environment(loader=PackageLoader('serve', 'templates'))

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

