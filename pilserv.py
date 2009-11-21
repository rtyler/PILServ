#!/usr/bin/env python

import cStringIO
import Image
import os
import sys
import time

from eventlet import api
from eventlet.green import BaseHTTPServer

class TransformException(Exception):
    pass

class BaseTransform(object):
    command = None
    @classmethod
    def execute(cls, path, out):
        raise TransformException('Subclasses of BaseTransform must override execute()')

class Resize(BaseTransform):
    @classmethod
    def execute(cls, path, out):
        im = Image.open('python.png')
        im.thumbnail((16, 16))
        im.save(out, 'png')

class PILHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        out = cStringIO.StringIO()
        print ('do_GET', self.__dict__)

        Resize.execute(None, out)
        data = out.getvalue()
        
        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(data))
        self.end_headers()

        self.wfile.write(data)


def main():
    try:
        address = ('', 8080,)
        server = BaseHTTPServer.HTTPServer(address, PILHandler)
        server.serve_forever()
    except:
        return -1
    return 0

if __name__ == '__main__':
    sys.exit(main())

