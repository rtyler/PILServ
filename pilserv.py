#!/usr/bin/env python

import os
import sys
import time

from eventlet import api
from eventlet.green import BaseHTTPServer

INBOUND_SIZE = 4096

class PILHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        print ('do_GET', self.__dict__)
        out = self.wfile
        data = ''
        with open('python.png', 'r') as fd:
            data = fd.read()
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        out.write(data)

def main():
    address = ('', 8080,)
    server = BaseHTTPServer.HTTPServer(address, PILHandler)
    server.serve_forever()

if __name__ == '__main__':
    sys.exit(main())

