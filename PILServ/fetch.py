#!/usr/bin/env python

from eventlet.green import urllib2


def __url(url):
    buf = None
    try:
        buf = urllib2.urlopen(url)
        return buf.read()
    finally:
        if buf:
            buf.close()

def fetchBuffer(url, cache=True):
    # Fetch image 
    return __url(url)

