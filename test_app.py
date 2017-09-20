#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

import unittest
import logging

from tornado.testing import AsyncHTTPTestCase

from app import make_app, init_redis


class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        init_redis()
        logging.getLogger('tornado.access').disabled = True
        logging.getLogger('tornado.general').disabled = True
        return make_app()

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_homepage(self):
        response = self.fetch('/', method="POST", body="")
        self.assertEqual(response.code, 405)

    def test_404(self):
        response = self.fetch('/notfound', method="GET")
        self.assertEqual(response.code, 404)

    def test_cehckupdate_400(self):
        response = self.fetch('/check_update', method="GET")
        self.assertEqual(response.code, 400)

    def test_cehckupdate_404(self):
        response = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response.code, 404)

    def test_cehckupdate_404_1(self):
        response = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response.code, 404)

    def test_cehckupdate_404_2(self):
        response = self.fetch('/check_update?app_id=5&version=0', method="GET")
        self.assertEqual(response.code, 404)

    def test_cehckupdate_200_1(self):
        response = self.fetch('/check_update?app_id=4&version=1.1.2', method="GET")
        self.assertEqual(response.code, 200)
        response = self.fetch('/check_update?app_id=4&version=1.1.2', method="GET")
        self.assertEqual(response.code, 200)
        self.assertIn("Hit From Redis", str(response.headers))


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
