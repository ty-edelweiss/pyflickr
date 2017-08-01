#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers

__version__ = "0.0.0"
__cwd__ = os.getcwd()

__format__ = "%(asctime)s %(levelname)s %(name)s: %(message)s"

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter(__format__))

file_handler = logging.handlers.RotatingFileHandler(
    filename = __cwd__ + "/logs/app.log",
    maxBytes = 1000,
    backupCount = 3,
    encoding = "utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(__format__))

logging.getLogger(__name__).addHandler(stream_handler)
logging.getLogger(__name__).addHandler(file_handler)
logging.getLogger(__name__).setLevel(logging.DEBUG)
