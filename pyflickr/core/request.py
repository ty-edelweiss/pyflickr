#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import queue
import threading
import requests
from typing import List, Dict, Any
from .manager import Validator


class Accessor(threading.Thread):

    url = "https://api.flickr.com/services/rest/"

    def __init__(self, cache: List[queue.Queue], notice: threading.Event, payload: Dict[str, Any], oauth: object = None, validator: object = None):
        super(Accessor, self).__init__()
        self.logger_ = logging.getLogger(__name__)
        self.validator_ = validator if validator else Validator()
        self.cache_ = cache
        self.notice_ = notice
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
            if not self.notice_.is_set() and self.validator_.status_ == "health":
                response = requests.get(Accessor.url, params=self.payload_, auth=self.oauth_)
                try:
                    self.validator_.check(response.text)
                    self.logger_.info(f"Access success to {Accessor.url} at {self.payload_['page']}")
                    for cache in self.cache_:
                        cache.put(response.text)
                except ValueError as err:
                    self.logger_.info(err)
                self.payload_["page"] = self.payload_["page"] + 1
                time.sleep(1)
            else:
                self.payload_["page"] = 1
                self.validator_.reset()
                self.notice_.set()
                break

        self.logger_.info("Api accessor shutdown")
