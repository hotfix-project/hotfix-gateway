#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import os
import sys
import uuid
import base64
import binascii
import json

try:
    import tornado.ioloop
    import tornado.web
    from tornado.options import define, options
except ImportError:
    print("logstorage service need tornado, please run depend.sh")
    sys.exit(1)


define('debug', default=True, help='enable debug mode')
define("port", default=8000, help="run on the given port", type=int)
define("bind", default='0.0.0.0', help="run on the given ipaddr", type=str)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


def make_app():
    settings = {
        'debug': options.debug,
    }

    return tornado.web.Application([
        (r'/', MainHandler),
    ], **settings)


def main():
    tornado.options.parse_command_line()
    app = make_app()
    sockets = tornado.netutil.bind_sockets(options.port, options.bind, reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
