#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import queue
import signal
import logging
import threading
import datetime
from optparse import OptionParser

from pyflickr.core import oauth
from pyflickr.core.mapper import FileAppender, DatabaseAppender
from pyflickr.core.request import Accessor
from pyflickr.core.manager import DateManager, Validator

VENDOR = "flickr"
CLASS = "photos"
METHOD = "search"

logger = logging.getLogger(__name__)
notice = threading.Event()
parser = OptionParser()

parser.add_option(
    "-s", "--start",
    type="string",
    help="collecting start date. mysql format date.",
    dest="start"
)

parser.add_option(
    "-e", "--end",
    type="string",
    help="collecting end date. mysql format date.",
    dest="end"
)

parser.add_option(
    "-t", "--time",
    action="store_true",
    default=False,
    help="changing input date is mysql format datetime.",
    dest="time"
)


def signalHandler(signal, frame):
    notice.set()
    logger.info("terminate crawling application.")
    sys.exit(1)


def validate(date_string: str, time_flag: bool):
    format = {
        "date": "%Y-%m-%d",
        "datetime": "%Y-%m-%d %H:%M:%S"
    }
    if not time_flag:
        try:
            dt = datetime.datetime.strptime(date_string, format["date"])
        except ValueError as err:
            logger.error(f"{date_string} does not match format(%Year-%month-%date)")
            sys.exit(1)
    else:
        try:
            dt = datetime.datetime.strptime(date_string, format["datetime"])
        except ValueError as err:
            logger.error(f"{date_string} does not match format(%Year-%month-%date %Hours:%Minutes:%Seconds)")
            sys.exit(1)
    return datetime.datetime.strftime(dt, format["datetime"])


if __name__ == "__main__":

    api = VENDOR + "." + CLASS + "." + METHOD
    options, args = parser.parse_args()

    if options.start is not None:
        options.start = validate(options.start, options.time)
    else:
        options.start = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    if options.end is not None:
        options.end = validate(options.end, options.time)

    token = oauth.auth()

    date_manager = DateManager(options.start, options.end)

    payload = {
        "method": api,
        "format": "json",
        "nojsoncallback": 1,
        "place_id": "W3QedCZTUb5Ez.rF.Q",
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

    signal.signal(signal.SIGINT, signalHandler)

    for min_date, max_date in date_manager:
        payload["min_upload_date"] = min_date
        payload["max_upload_date"] = max_date
        accessor = Accessor([ queue ], notice, payload, token)
        appender = FileAppender(queue, notice, "data/" + min_date.split(" ")[0] + ".json")
        accessor.start()
        appender.start()
        accessor.join()
        appender.join()
        notice.clear()
