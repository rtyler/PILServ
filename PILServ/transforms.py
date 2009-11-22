#!/usr/bin/env python

import Image
import sys

from StringIO import StringIO

class TransformException(Exception):
    pass

class BaseTransform(object):
    command = None
    @classmethod
    def execute(cls, infile, args, **kwargs):
        args = cls.parsePositionals(args)
        return cls._execute(infile, *args, **kwargs)

    @classmethod
    def parsePositionals(cls, rawbuf):
        if not rawbuf:
            return []
        return [p.strip() for p in rawbuf[1:-1].split(',')]

class Resize(BaseTransform):
    command = 'resize'
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


class Rotate(BaseTransform):
    command = 'rotate'
    @classmethod
    def _execute(cls, infile, angle, **kwargs):
        outfile = StringIO()
        im = Image.open(infile)
        im = im.rotate(float(angle), expand=True)
        im.save(outfile, 'png')
        return outfile.getvalue()

class Flip(Rotate):
    command = 'flip'
    @classmethod
    def _execute(cls, infile, *args, **kwargs):
        return Rotate._execute(infile, 180, **kwargs)


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

commands = dict(((t.command, t) for t in __aggregate()))

