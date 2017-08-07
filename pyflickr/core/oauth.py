#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import urllib.parse
import webbrowser
import requests
from requests_oauthlib import OAuth1
from xml.dom import minidom
from xml.etree import ElementTree
from typing import Dict, Tuple, Any

from ..util.utils import xmlToTreeDict, treeDictToXml

__cwd__ = os.getcwd()

logger = logging.getLogger(__name__)

vendor_config = {
    "REQUEST_URL": "https://www.flickr.com/services/oauth/request_token",
    "AUTHORIZE_URL": "https://www.flickr.com/services/oauth/authorize",
    "ACCESS_TOKEN_URL": "https://www.flickr.com/services/oauth/access_token",
    "CALLBACK_URI": "oob"
}


def oauth_request(api_key: str, api_secret: str) -> Dict[str, Any]:
    logger.info(f"Success loading the authentication of flickr vendor_config.")
    request_url, authorize_url, access_token_url = vendor_config["REQUEST_URL"], vendor_config["AUTHORIZE_URL"], vendor_config["ACCESS_TOKEN_URL"]
    callback_uri = vendor_config["CALLBACK_URI"]
    auth = OAuth1(api_key, api_secret, callback_uri=callback_uri)
    response = requests.post(request_url, auth=auth)
    request_token = dict(urllib.parse.parse_qsl(response.text))
    logger.info(f"Success get to request token on this crawling application by {request_url}")

    webbrowser.open(f"{authorize_url}?oauth_token={request_token['oauth_token']}&perms=delete")
    oauth_verifier = input("Please input PIN code : ")
    auth = OAuth1(
        api_key,
        api_secret,
        request_token["oauth_token"],
        request_token["oauth_token_secret"],
        verifier=oauth_verifier
    )
    response = requests.post(access_token_url, auth=auth)
    access_token = dict(urllib.parse.parse_qsl(response.text))
    logger.info(f"Success get to access token on this crawling application by {access_token_url}")
    return access_token


def oauth_validator() -> Tuple[str, str, Dict[str, Any]]:
    config_path = __cwd__ + "/config/application.conf"
    if os.path.isfile(config_path):
        with open(config_path, "r") as fp:
            lines = fp.readlines()
            consumer_key, consumer_secret = tuple([line.strip().split("=")[1] for line in lines if "=" in line])
        config = {
            "api": {
                "@secret": consumer_secret,
                "token": {
                    "text": None,
                    "@secret": None
                }
            }
        }
        if not consumer_key and not consumer_secret:
            raise ValueError("api cofiguration is invalid")
    else:
        raise ValueError("api cofiguration file is not exist")
    return consumer_key, consumer_secret, config


def auth() -> object:
    api_key, api_secret, config = oauth_validator()
    api_path = __cwd__ + "/tmp/" + api_key + ".xml"
    if os.path.isfile(api_path):
        tree = ElementTree.parse(api_path)
        api_config = xmlToTreeDict(tree.getroot())
        if api_config["api"]["token"]["text"] and api_config["api"]["token"]["@secret"]:
            return OAuth1(api_key, api_secret, api_config["api"]["token"]["text"], api_config["api"]["token"]["@secret"])
        else:
            access_token = oauth_request(api_key, api_secret)
            api_config["api"]["token"]["text"] = access_token["oauth_token"]
            api_config["api"]["token"]["@secret"] = access_token["oauth_token_secret"]
            root = treeDictToXml(api_config)
            xml_string = minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent="  ")
            with open(api_path, "w", encoding="utf-8") as fp:
                fp.write(xml_string)
    else:
        access_token = oauth_request(api_key, api_secret)
        config["api"]["token"]["text"] = access_token["oauth_token"]
        config["api"]["token"]["@secret"] = access_token["oauth_token_secret"]
        root = treeDictToXml(config)
        xml_string = minidom.parseString(ElementTree.tostring(root)).toprettyxml(indent="  ")
        with open(api_path, "w", encoding="utf-8") as fp:
            fp.write(xml_string)
    return OAuth1(api_key, api_secret, access_token["oauth_token"], access_token["oauth_token_secret"])

