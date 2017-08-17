#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import os
import sys
import uuid
import base64
import binascii
import json
import redis
import logging

logger = logging.getLogger(__name__)

try:
    import tornado.ioloop
    import tornado.web
    import tornado.httpclient
    from tornado.options import parse_command_line, define, options
    from tornado.web import HTTPError, asynchronous
except ImportError:
    print("logstorage service need tornado, please run depend.sh")
    sys.exit(1)

try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient
except ImportError:
    from tornado.simple_httpclient import SimpleAsyncHTTPClient as AsyncHTTPClient


redis_context = {}

define('debug', default=True, help='enable debug mode')
define("port", default=8001, help="run on the given port", type=int)
define("bind", default='0.0.0.0', help="run on the given ipaddr", type=str)
define("redis_host", default='127.0.0.1', help="redis server ipaddr", type=int)
define("redis_port", default=6379, help="reids server port", type=str)
define("backend_scheme", default='http', help="redis server ipaddr", type=str)
define("backend_host", default='192.168.1.193', help="redis server ipaddr", type=str)
define("backend_port", default=8000, help="reids server port", type=int)
define("max_clients", default=20, help="async http client max clients", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = {
            "check_update": "http://%s/check_update" % (self.request.host),
            "report_update": "http://%s/report_update" % (self.request.host),
            "custom_check_update": "http://%s/check_update" % (self.request.host),
            "custom_report_update": "http://%s/report_update" % (self.request.host),
        }
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data))

    def compute_etag(self):
        return None


class ProxyHandler(tornado.web.RequestHandler):
    @asynchronous
    def get(self):
        self._do_fetch('GET')

    def _do_fetch(self, method):
        uri = self.request.uri
        url = "%s://%s:%s%s?%s" % (
            options.backend_scheme, 
            options.backend_host,
            options.backend_port,
            uri,
            self.request.query
        )
        headers = dict(self.request.headers)
        try:
            AsyncHTTPClient(max_clients=options.max_clients).fetch(
                tornado.httpclient.HTTPRequest(url=url,
                            method=method,
                            body=None,
                            headers=headers,
                            follow_redirects=False),
                self._on_proxy)
        except HTTPError as x:
            if hasattr(x, "response") and x.response:
                self._on_proxy(x.response)
            else:
                logger.error("Tornado signalled HTTPError %s", x)

    def _on_proxy(self, response):
        self.write(response.body)
        self.finish()

    def compute_etag(self):
        return None


def init_redis(context):
    pool = redis.ConnectionPool(host=options.redis_host, port=options.redis_port, max_connections=10)
    rds = redis.Redis(connection_pool=pool)
    try:
        rds.info()
    except redis.exceptions.ConnectionError as e:
        logger.error(e)
        sys.exit(1)
    context["pool"] = pool
    context["rds"] = rds


def make_app():
    settings = {
        'debug': options.debug,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/custom_check_update', ProxyHandler),
        (r'/custom_report_update', ProxyHandler),
        (r'/check_update', ProxyHandler),
        (r'/report_update', ProxyHandler),
    ], **settings)


def main():
    parse_command_line()
    init_redis(redis_context)
    logger.info("listen: %s:%d, pid: %s, redis version: %s", 
        options.bind,
        options.port,
        redis_context["pool"].pid,
        redis_context["rds"].info()["redis_version"]
    )
    app = make_app()
    sockets = tornado.netutil.bind_sockets(options.port, options.bind, reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
