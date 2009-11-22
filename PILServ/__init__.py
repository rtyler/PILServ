#!/usr/bin/env python

import logging
import os
import re

from StringIO import StringIO

from eventlet import api
from eventlet.green import BaseHTTPServer

from PILServ import fetch
from PILServ import transforms

if os.getenv('DEBUG'):
    logging.basicConfig(level=logging.DEBUG) 

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
            # No URL parsed out!
            return # XXX: Error condition

        image = m.group(1)

        # Grab the precending commands from the URL
        rest = self.path[:-(len(image))]
        commands = rest.split('/')

        # Fetch a string buffer representing the image
        image = fetch.fetchBuffer(image)

        # Chain commands together
        for command in commands:
            if not command:
                continue
            args = self.arguments_regex.search(command)
            if args:
                args = args.group(1)
                # `command` is formatted like "resize(32x32)" here, 
                # strip off the latter bits
                command = command[:-(len(args))]

            command = transforms.commands.get(command)
            if not command:
                continue

            image = command().execute(StringIO(image), args)

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

