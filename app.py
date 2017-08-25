#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import os
import sys
import uuid
import base64
import binascii
import json
import redis

try:
    import tornado.ioloop
    import tornado.web
    import tornado.httpclient
    from tornado.options import parse_command_line, define, options
except ImportError:
    print("logstorage service need tornado, please run depend.sh")
    sys.exit(1)

redis_context = {}

define('debug', default=True, help='enable debug mode')
define("port", default=8000, help="run on the given port", type=int)
define("bind", default='0.0.0.0', help="run on the given ipaddr", type=str)
define("redis_host", default='127.0.0.1', help="redis server ipaddr", type=int)
define("redis_port", default=6379, help="reids server port", type=str)
define("backend_scheme", default='http', help="redis server ipaddr", type=str)
define("backend_host", default='172.28.32.101', help="redis server ipaddr", type=str)
define("backend_port", default=8000, help="reids server port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        data = {
            "check_update": "http://172.28.32.103:%s/check_update" % (options.port),
            "report_update": "http://172.28.32.103:%s/report_update" % (options.port),
        }
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(data))

    def compute_etag(self):
        return None


class CheckUpdateHandler(tornado.web.RequestHandler):
    def get(self):
        endpoint = "/custom_check_update"
        http_client = tornado.httpclient.HTTPClient()
        url = "%s://%s:%s%s?%s" % (options.backend_scheme, options.backend_host, options.backend_port, endpoint, self.request.query)
        response = http_client.fetch(url)
        self.write(response.body)

    def compute_etag(self):
        return None


class ReportUpdateHandler(tornado.web.RequestHandler):
    def get(self):
        endpoint = "/custom_report_update"
        http_client = tornado.httpclient.HTTPClient()
        url = "%s://%s:%s%s?%s" % (options.backend_scheme, options.backend_host, options.backend_port, endpoint, self.request.query)
        response = http_client.fetch(url)
        self.write(response.body)

    def compute_etag(self):
        return None


def init_redis(context):
    pool = redis.ConnectionPool(host=options.redis_host, port=options.redis_port, max_connections=10)
    rds = redis.Redis(connection_pool=pool)
    try:
        print("redis_version:", rds.info()["redis_version"])
    except redis.exceptions.ConnectionError as e:
        print(e)
        sys.exit(1)
    context["pool"] = pool
    context["rds"] = rds


def make_app():
    settings = {
        'debug': options.debug,
    }

    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/check_update', CheckUpdateHandler),
        (r'/report_update', ReportUpdateHandler),
    ], **settings)


def main():
    parse_command_line()
    init_redis(redis_context)
    # print(redis_context["pool"].pid, redis_context["rds"].info()["redis_version"])
    app = make_app()
    sockets = tornado.netutil.bind_sockets(options.port, options.bind, reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
