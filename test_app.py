#!/usr/bin/env python3.6
# -*- coding: UTF-8 -*-

'''
>>> from tornado.testing import AsyncHTTPTestCase
>>> dir(AsyncHTTPTestCase)
'''

import unittest
import logging
import os
import sys

from tornado.testing import AsyncHTTPTestCase

from app import make_app, init_redis, flush_redis

BIN_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BIN_DIR, 'misc/encrypt'))
from encrypt_json import encrypt_result, decrypt_result

key = 'd4f7d2adf42c34a3'
iv = "5c6ca7c26b1b068d"



class TestHelloApp(AsyncHTTPTestCase):
    def get_app(self):
        init_redis()
        flush_redis()
        logging.getLogger('tornado.access').disabled = True
        logging.getLogger('tornado.general').disabled = True
        return make_app()

    def test_404(self):
        response = self.fetch('/notfound', method="GET")
        self.assertEqual(response.code, 404)

    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_homepage_405(self):
        response = self.fetch('/', method="POST", body="")
        self.assertEqual(response.code, 405)

    def test_checkupdate_400(self):
        response_1 = self.fetch('/check_update', method="GET")
        self.assertEqual(response_1.code, 400)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/check_update', method="GET")
        self.assertEqual(response_2.code, 400)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_reportupdate_400(self):
        response_1 = self.fetch('/report_update', method="GET")
        self.assertEqual(response_1.code, 400)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/report_update', method="GET")
        self.assertEqual(response_2.code, 400)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_checkupdate_404(self):
        response_1 = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response_1.code, 404)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response_2.code, 404)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_reportupdate_404(self):
        response_1 = self.fetch('/report_update?patch_id=0', method="GET")
        self.assertEqual(response_1.code, 404)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/report_update?patch_id=0', method="GET")
        self.assertEqual(response_2.code, 404)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_checkupdate_404_1(self):
        response_1 = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response_1.code, 404)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/check_update?app_id=0', method="GET")
        self.assertEqual(response_2.code, 404)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_checkupdate_404_2(self):
        response_1 = self.fetch('/check_update?app_id=5&version=0', method="GET")
        self.assertEqual(response_1.code, 404)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/check_update?app_id=5&version=0', method="GET")
        self.assertEqual(response_2.code, 404)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_checkupdate_200_1(self):
        response_1 = self.fetch('/check_update?app_id=4&version=1.1.2', method="GET")
        self.assertEqual(response_1.code, 200)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/check_update?app_id=4&version=1.1.2', method="GET")
        self.assertEqual(response_2.code, 200)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)

    def test_reportupdate_200_1(self):
        response_1 = self.fetch('/report_update?patch_id=79', method="GET")
        self.assertEqual(response_1.code, 200)
        self.assertNotIn("Hit From Redis", str(response_1.headers))
        response_2 = self.fetch('/report_update?patch_id=79', method="GET")
        self.assertEqual(response_2.code, 200)
        self.assertIn("Hit From Redis", str(response_2.headers))
        self.assertEqual(response_1.body, response_2.body)


if __name__ == '__main__':
    unittest.main()


if __name__ == '__main__':
    unittest.main()
