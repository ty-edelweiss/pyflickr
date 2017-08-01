#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import logging
from pyflickr.core import oauth
from pyflickr.core.mapper import FileAppender
from pyflickr.core.request import Accessor
from pyflickr.core.manager import DateManager, Validator

VENDOR = "flickr"
CLASS = "photos"
METHOD = "search"

if __name__ == "__main__":

    api = VENDOR + "." + CLASS + "." + METHOD

    token = oauth.auth()

    date_manager = DateManager("2016-1-1 00:00:00")

    payload = {
        "method": api,
        "format": "json",
        "nojsoncallback": 1,
        "extras": "description, license, date_upload, date_taken"\
                  "owner_name, icon_server, original_format, last_update"\
                  "geo, tags, machine_tags, o_dims"\
                  "views, media path_alias, url_sq"\
                  "url_t, url_s, url_q, url_m"\
                  "url_n, url_z, url_c, url_l, url_o",
        "per_page": 200,
        "page": 1
    }

    queue = queue.Queue()

    for min_date, max_date in date_manager:
        payload["min_taken_date"] = min_date
        payload["max_taken_date"] = max_date
        notice = True
        accessor = Accessor(queue, notice, payload, token)
        appender = FileAppender(queue, notice, "data/" + min_date.split(" ")[0] + ".json")
        accessor.start()
        print("accessor")
        appender.start()
        print("appender")
        accessor.join()
        print("accessor")
        appender.join()
        print("appender")
