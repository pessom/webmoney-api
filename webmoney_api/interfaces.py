#-*- coding: utf-8 -*-
from lxml import etree
import requests as r
from pprint import pprint, pformat
import uuid
import xmltodict


class AuthInterface(object):

    """
    Интерфейс аунтефикации
    """

    def wrap_request(request_params):
        """

        """
        return request_params

    def wrap_body_tree(self, tree):
        """

        """
        return tree

    def get_url_by_name(self, name):
        raise NotImplemented


class WMLightAuthInterface(AuthInterface):

    def __init__(self, pub_cert, priv_key=None):
        self.cert = pub_cert if priv_key is None else (pub_cert, priv_key)

    def wrap_request(self, request_params):
        request_params.update({"cert": self.cert})
        return request_params

    def get_url_by_name(self, name):
        if name == "FindWMPurseNew":
            return "https://w3s.wmtransfer.com/asp/XMLFindWMPurseCertNew.asp"
        return "https://w3s.wmtransfer.com/asp/XML{}Cert.asp".format(name)


class ApiInterface(object):

    """

    """

    API_METADATA = {"FindWMPurseNew": {"root_name": "testwmpurse",
                                       "aliases": ["x8"]},
                    "Purses": {"root_name": "getpurses",
                               "aliases": ["x9"]},
                    "Invoice": {"root_name": "invoice",
                                "aliases": ["x1"]},
                    "Trans": {"root_name": "trans",
                              "aliases": ["x2"]},
                    "Operations": {"root_name": "getoperations",
                                   "aliases": ["x3"]},
                    "OutInvoices": {"root_name": "getoutinvoices",
                                    "aliases": ["x4"]},
                    "FinishProtect": {"root_name": "finishprotect",
                                      "aliases": ["x5"]},
                    "SendMsg": {"root_name": "message",
                                "aliases": ["x6"]},
                    "ClassicAuth": {"root_name": "testsign",
                                    "aliases": ["x7"]},
                    "InInvoices": {"root_name": "getininvoices",
                                   "aliases": ["x10"],
                                   "response_name": "ininvoices"}}
    """
    Метаданные интерфейсов API Webmoney.
    Имеют следующую структуру::

    	{<interface_name>:{
    		"root_name": <root_name>, 
    		"aliases": [<string>, <string>, ...], 
    		"response_name": <response_name>
    	}}

    Параметры имеют следующий смысл:

    :param interface_name: Название интерфейса в URL, например, для X9 (https://w3s.webmoney.ru/asp/XMLPurses.asp) названием будет Purses. Название используется при конструировании урла 
    :param root_name: название рутового элемента секции данных запроса 
    :param response_name: Название рутового элемента секции данных ответа(если не задан, берется **root_name**)

    """

    def __init__(self, authenticationStrategy):
        self.authStrategy = authenticationStrategy

    def _check_params(self, params):
        for key, value in params:
            assert key in self.API_METADATA

    def _get_root_name_by_interface_name(self, interface_name):
        assert interface_name in self.API_METADATA, "Incorrect interface name: %s" % interface_name
        return self.API_METADATA[interface_name]["root_name"]

    def _create_xml_request_params(self, interface_name, params):
        """
        Создает подзапрос, различающийся для каждого WM интерфейса
        :param interface_name: Название интерфейса
        :param params: Словарь аргументов
        """
        root_name = self._get_root_name_by_interface_name(interface_name)
        tree = etree.Element(root_name)
        for key, value in params.iteritems():
            subelement = etree.Element(key)
            subelement.text = value
            tree.append(subelement)

        return tree

    def _create_request(self, interface, **kwargs):
        """
        Создает запрос к api
        """
        request_params = {
            "url": self.authStrategy.get_url_by_name(interface), "verify": False}

        request_params = self.authStrategy.wrap_request(request_params)

        return request_params

    def _create_body(self, interface, **params):

        tree = etree.Element("w3s.request")

        reqn = params.pop("reqn", None)
        _ = etree.Element("reqn")

        if reqn:
            _.text = str(int(reqn))
        else:
            _.text = ""

        tree.append(_)

        tree.append(self._create_xml_request_params(interface, params))

        tree = self.authStrategy.wrap_body_tree(tree)

        return etree.tostring(tree)

    def _make_request(self, interface, **params):
        request_params = self._create_request(interface, **params)
        body = self._create_body(interface, **params)

        request_params.update({"data": body})

        response = r.post(**request_params)

        if response.status_code != 200:
            print "Something bad:"
            print "Request status code:", response.status_code
            print "Response:"
            print response.text
            exit(1)

        out = xmltodict.parse(response.text)["w3s.response"]
        # print out
        # print self.API_METADATA[interface]["root_name"]

        try:
            response_name = self.API_METADATA[interface].get(
                "response_name", None) or self.API_METADATA[interface]["root_name"]
            resp = out[response_name]
        except:
            out = u"Error while requesting API. retval = %s, retdesc = %s" % (
                out["retval"], out["retdesc"]) + "\n" +\
                u"Request примет data: %s" % pformat(request_params)
            raise ValueError(out.encode("utf-8"))
            exit(1)

        return {"retval": out["retval"],
                "retdesc": out["retdesc"],
                "response": resp}

    def __getattribute__(self, name):
        if name in ApiInterface.API_METADATA.keys():
            def _callback(**params):
                return self._make_request(name, **params)

            return _callback

        for key, aliases in ApiInterface.API_METADATA.iteritems():
            aliases = aliases["aliases"]
            if name.lower() in aliases:
                def _callback(**params):
                    return self._make_request(key, **params)
                return _callback

        return object.__getattribute__(self, name)

print ApiInterface(WMLightAuthInterface("/home/stas/wmcerts/crt.pem", "/home/stas/wmcerts/key.pem")).x4(
    wmid="407414370132", reqn="100", datestart="20100101 00:00:00", datefinish="20140501 00:00:00")["response"]["ininvoice"]
