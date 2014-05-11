#-*- coding: utf-8 -*-
import unittest
from webmoney_api.interfaces import ApiInterface, AuthInterface
from lxml import etree


class TestApiInterface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = ApiInterface(AuthInterface())

    def test__create_xml_request_params(self):

        xml = self.api._create_xml_request_params(
            "FindWMPurseNew", {"wmid": "olala",
                               "purse": "123"})

        self.assertEqual(
            etree.tostring(xml), "<testwmpurse><wmid>olala</wmid><purse>123</purse></testwmpurse>")
