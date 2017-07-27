#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import queue
import threading
import urllib.parse
import webbrowser
import requests
from requests_oauthlib import OAuth1
from xml.dom import minidom
from xml.etree import ElementTree
from typing import Dict, Any
from .manager import Validator
from ..util.utils import xmlToTreeDict, treeDictToXml


class OAuth(object):

    configure = {
        "REQUEST_URL": "https://www.flickr.com/services/oauth/request_token",
        "AUTHORIZE_URL": "https://www.flickr.com/services/oauth/authorize",
        "ACCESS_TOKEN_URL": "https://www.flickr.com/services/oauth/access_token",
        "CALLBACK_URI": "oob"
    }

    def __init__(self, api_key: str, api_secret: str):
        self.logger_ = logging.getLogger(__name__)
        self.api_key_ = api_key
        self.api_secret_ = api_secret

    def oauth_request(self):
        self.logger_.info(f"Success loading the authentication of flickr configure.")
        request_url, authorize_url, access_token_url = OAuth.configure["REQUEST_URL"], OAuth.configure["AUTHORIZE_URL"], OAuth.configure["ACCESS_TOKEN_URL"]
        callback_uri = OAuth.configure["CALLBACK_URI"]
        auth = OAuth1(self.api_key_, self.api_secret_, callback_uri=callback_uri)
        response = requests.post(request_url, auth=auth)
        request_token = dict(urllib.parse.parse_qsl(response.text))
        self.logger_.info(f"Success get to request token on this crawling application by {request_url}")

        webbrowser.open(f"{authorize_url}?oauth_token={request_token['oauth_token']}&perms=delete")
        oauth_verifier = input("Please input PIN code : ")
        auth = OAuth1(
            self.api_key_,
            self.api_secret_,
            request_token["oauth_token"],
            request_token["oauth_token_secret"],
            verifier=oauth_verifier
        )
        response = requests.post(access_token_url, auth=auth)
        access_token = dict(urllib.parse.parse_qsl(response.text))
        self.logger_.info(f"Success get to access token on this crawling application by {access_token_url}")
        return access_token

    def auth(self) -> object:
        config_path = "../tmp/" + self.api_key_ + ".xml"
        if os.path.isfile(config_path):
            tree = ElementTree.parse(config_path)
            config = xmlToTreeDict(tree.getroot())
            if config["api"]["token"]["text"] and config["api"]["token"]["@secret"]:
                return OAuth1(self.api_key_, self.api_secret_, config["api"]["token"]["text"], config["api"]["token"]["@secret"])
            else:
                access_token = self.oauth_request()
                print(access_token)
                config["api"]["token"]["text"] = access_token["oauth_token"]
                config["api"]["token"]["@secret"] = access_token["oauth_token_secret"]
                root = treeDictToXml(config)
                xml_string = minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent="  ")
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write(xml_string)
        else:
            access_token = self.oauth_request()
        return OAuth1(self.api_key_, self.api_secret_, access_token["oauth_token"], access_token["oauth_token_secret"])


class Accessor(threading.Thread):

    url = "https://api.flickr.com/services/rest/"

    def __init__(self, cache: queue.Queue, notice: bool, payload: Dict[str, Any], oauth: object):
        super(Accessor, self).__init__()
        self.logger_ = logging.getLogger(__name__)
        self.validator_ = Validator()
        self.cache_ = cache
        self.flag_ = notice
        self.payload_ = payload
        self.oauth_ = oauth
        self.running_ = False

    def kill(self) -> object:
        self.running_ = False
        return self

    def run(self) -> None:
        self.running_ = True

        self.logger_.info("Api accessor running ... ")
        while self.running_:
            if self.validator_.status_:
                response = requests.get(Accessor.url, params=self.payload_, auth=self.oauth_)
                try:
                    self.validator_.check(response)
                    self.logger_.info(f"Access success to {Accessor.url} at {self.payload_['page']}")
                    self.cache_.put(response.text)
                except ValueError as err:
                    self.logger_.info(err)
                self.payload_["page"] = self.payload_["page"] + 1
                time.sleep(1)
            else:
                self.flag_ = True
                break

        self.logger_.info("Api accessor shutdown")
