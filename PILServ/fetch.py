#!/usr/bin/env python
from __future__ import with_statement

import os
import logging

from eventlet.green import urllib2

CACHE_DIR = os.path.sep + os.path.join('tmp', 'pilserv')

def __url(url):
    buf = None
    try:
        buf = urllib2.urlopen(url)
        return buf.read()
    finally:
        if buf:
            buf.close()

def __cacheFile(url):
    # Doing a basic hash for now, might get more complicated later
    return os.path.join(CACHE_DIR, str(hash(url)))

def __cachedBuffer(url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    cached = __cacheFile(url)
    if not os.path.exists(cached):
        return None

    with open(cached, 'r') as fd:
        return fd.read()
    

def __cacheBuffer(url, data):
    path = __cacheFile(url)
    with open(path, 'w') as fd:
        fd.write(data)

def fetchBuffer(url, cache=True):
    if cache:
        cached = __cachedBuffer(url)
        if cached:
            logging.debug('Cache hit for: %s' % url)
            return cached
        logging.debug('Cache miss for: %s' % url)

    # Fetch image 
    rc = __url(url)
    if cache:
        __cacheBuffer(url, rc)
    return rc

