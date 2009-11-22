#!/usr/bin/env python

import Image
import os
import re
import pdb
import sys
import time

from StringIO import StringIO

from eventlet import api
from eventlet.green import urllib2
from eventlet.green import BaseHTTPServer

class TransformException(Exception):
    pass

class BaseTransform(object):
    command = None
    @classmethod
    def execute(cls, path, out):
        raise TransformException('Subclasses of BaseTransform must override execute()')

    @classmethod
    def parsePositionals(cls, rawbuf):
        if not rawbuf:
            return []
        return [p.strip() for p in rawbuf[1:-1].split(',')]

class Resize(BaseTransform):
    command = 'resize'
    @classmethod
    def execute(cls, infile, args, **kwargs):
        args = cls.parsePositionals(args)
        return cls._execute(infile, *args, **kwargs)

    @classmethod
    def _execute(cls, infile, size, **kwargs):
        if not size:
            size = (64, 64)
        else:
            size = tuple(size.split('x'))
        outfile = StringIO()
        im = Image.open(infile)
        im.thumbnail(size)
        im.save(outfile, 'png')
        return outfile.getvalue()

class Flip(BaseTransform):
    command = 'flip'
    @classmethod
    def execute(cls, infile, args, **kwargs):
        args = cls.parsePositionals(args)
        return cls._execute(infile, *args, **kwargs)

    @classmethod
    def _execute(cls, infile, *args, **kwargs):
        outfile = StringIO()
        im = Image.open(infile)
        im = im.rotate(180, expand=True)
        im.save(outfile, 'png')
        return outfile.getvalue()

def __aggregate():
    module = sys.modules[__name__]
    for name in dir(module):
        attr = getattr(module, name)
        if not isinstance(attr, type):
            continue
        if not issubclass(attr, BaseTransform):
            continue
        if attr == BaseTransform:
            continue
        yield attr

transform_commands = dict(((t.command, t) for t in __aggregate()))

class PILHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    nongreedy = '.*?' 
    url_re = '((?:http|https)(?::\\/{2}[\\w]+)(?:[\\/|\\.]?)(?:[^\\s"]*))'
    url_regex = re.compile(nongreedy + url_re, re.IGNORECASE | re.DOTALL)
    args_re = '(\\(.*\\))'
    arguments_regex = re.compile(nongreedy + args_re, re.IGNORECASE | re.DOTALL)

    def do_GET(self, *args, **kwargs):
        print ('do_GET', self.__dict__)
        m = self.url_regex.search(self.path)
        if not m:
            return # XXX: Error condition
        image = m.group(1)

        rest = self.path[:-(len(image))]
        commands = rest.split('/')

        # Fetch image 
        fd = urllib2.urlopen(image)
        image = fd.read()
        fd.close()

        # Chain commands together
        for command in reversed(commands):
            if not command:
                continue
            args = self.arguments_regex.search(command)
            if args:
                args = args.group(1)
                command = command[:-(len(args))]
            command = transform_commands.get(command)

            if not command:
                continue

            image = command.execute(StringIO(image), args)

        self.send_response(200)
        self.send_header('Content-Type', 'image/png')
        self.send_header('Content-Length', len(image))
        self.end_headers()

        self.wfile.write(image)


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

