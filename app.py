#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import os
import sys
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
define("bind", default='0.0.0.0', help="run on the given ipaddr", type=str)
define("port", default=8001, help="run on the given port", type=int)
define("max_clients", default=20, help="async http client max clients", type=int)
define("redis_host", default='127.0.0.1', help="redis server ipaddr", type=int, group='redis')
define("redis_port", default=6379, help="reids server port", type=str, group='redis')
define("redis_ttl", default=60, help="reids key ttl", type=int, group='redis')
define("backend_scheme", default='http', help="backend server ipaddr", type=str, group='backend')
define("backend_host", default='127.0.0.1', help="backend server ipaddr", type=str, group='backend')
define("backend_port", default=8000, help="backend server port", type=int, group='backend')


class BaseHandler(tornado.web.RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        if status_code == 405:
            data = {
                "message": "method not allowed"
            }
        self.write(json.dumps(data))


class PageNotFound(BaseHandler):
    def get(self):
        self.set_status(404)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        data = {
            "message": "not found"
        }
        self.write(json.dumps(data))


class MainHandler(BaseHandler):
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


class ProxyHandler(BaseHandler):
    @asynchronous
    def get(self):
        rds = redis_context["rds"]
        if self.request.path == "/check_update":
            key = "status_%s" % (self.request.uri)
            status = rds.get(key)
            key = "response_%s" % (self.request.uri)
            response = rds.get(key)
            if response is not None and status is not None:
                self.set_header("X-Cache-Lookup", "Hit From Redis")
                if int(status) == 200:
                    data = json.loads(response)
                    released = data["result"]["patch"]["released"]
                    if len(released) == 1:
                        key = "patch_id=%d" % (data["result"]["patch"]["released"][0]["id"])
                        download_count = rds.hget("download_count_hash", key)
                        pool_size = rds.hget("pool_size_hash", key)
                        if int(download_count) > int(pool_size):
                            self.set_status(404)
                            self.write('{"message": "not found patch"}')
                            self.finish()
                            return
                        else:
                            rds.hincrby("download_count_hash", key)
                self.set_status(int(status))
                self.write(response)
                self.finish()
                return
            
        if self.request.path == "/report_update":
            key = "status_%s" % (self.request.uri)
            status = rds.get(key)
            key = "response_%s" % (self.request.uri)
            response = rds.get(key)
            if response is not None and status is not None:
                self.set_header("X-Cache-Lookup", "Hit From Redis")
                if int(status) == 200:
                    rds.hincrby("apply_count_hash", self.request.uri)
                self.set_status(int(status))
                self.write(response)
                self.finish()
                return
        self._do_fetch('GET')

    def _do_fetch(self, method):
        uri = self.request.uri
        url = "%s://%s:%s%s" % (
            options.backend_scheme,
            options.backend_host,
            options.backend_port,
            uri,
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

    def cache_check_update(self, status_code, response):
        print("cache_check_update")
        rds = redis_context["rds"]
        key = "status_%s" % (self.request.uri)
        rds.set(key, status_code, options.redis_ttl)
        key = "response_%s" % (self.request.uri)
        rds.set(key, response.body, options.redis_ttl)
        if status_code == 200:
            data = json.loads(response.body)
            released = data["result"]["patch"]["released"]
            if len(released) == 1:
                key = "patch_id=%s"%(released[0]["id"])
                pool_size = released[0]["pool_size"]
                rds.hset("pool_size_hash", key, pool_size)
                rds.hsetnx("download_count_hash", key, 0)
                rds.hincrby("download_count_hash", self.request.uri)

    def cache_report_update(self, status_code, response):
        rds = redis_context["rds"]
        key = "status_%s" % (self.request.uri)
        rds.set(key, status_code, options.redis_ttl)
        key = "response_%s" % (self.request.uri)
        rds.set(key, response.body, options.redis_ttl)
        rds.hsetnx("apply_count_hash", self.request.uri, 0)
        if status_code == 200:
            rds.hincrby("apply_count_hash", self.request.uri)

    def _on_proxy(self, response):
        self.clear()
        status_code = response.code==599 and 500 or response.code
        self.set_status(status_code)
        for k,v in dict(response.headers).items():
            self.set_header(k, v)
        if response.body is not None:
            self.write(response.body)
        else:
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            self.write('{"status": %s", "message": "internal server error"}' % (response.code))

        if self.request.path == "/check_update":
            self.cache_check_update(status_code, response)
        if self.request.path == "/report_update":
            self.cache_report_update(status_code, response)

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
        (r'/check_update', ProxyHandler),
        (r'/report_update', ProxyHandler),
        (r'.*', PageNotFound),
    ], **settings)


def main():
    parse_command_line()
    init_redis(redis_context)
    logger.info("listen: %s:%d, pid: %s, redis version: %s",
        options.bind,
        options.port,
        redis_context["pool"].pid,
        redis_context["rds"].info()["redis_version"])
    app = make_app()
    sockets = tornado.netutil.bind_sockets(options.port, options.bind, reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
