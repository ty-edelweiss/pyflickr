#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import queue
import threading
import psycopg2
from typing import Dict, Any

__cwd__ = os.getcwd()

class FileAppender(threading.Thread):

    def __init__(self, cache: queue.Queue, notice: threading.Event, path: str):
        super(FileAppender, self).__init__()
        self.logger_ = logging.getLogger(__name__)
        self.cache_ = cache
        self.notice_ = notice
        self.path_ = __cwd__ + "/" + path
        self.running_ = False

    def kill(self) -> object:
        self.running_ = True
        return self

    def run(self) -> None:
        self.running_ = True

        self.logger_.info("File appender running ... ")
        while self.running_:
            if not self.notice_.is_set():
                data = self.cache_.get()
                with open(self.path_, "a") as f:
                    f.write(data)
                self.logger_.info(f"Append success to {self.path_}")
            else:
                break

        self.logger_.info("File appender shutdown")


class DatabaseAppender(object):

    def __init__(self, cache: queue.Queue, notice: threading.Event, config: Dict[str, Any]):
        super(DatabaseAppender, self).__init__()
        self.logger_ = logging.getLogger(__name__)
        self.cache_ = cache
        self.notice_ = notice
        self.connection_ = psycopg2.connect(**config)
        self.running_ = False

    def kill(self) -> object:
        self.running_ = True
        return self

    def run(self) -> None:
        self.running_ = True

        cursor = self.connection_.cursor()

        self.logger_.info("Database appender running ... ")
        while self.running_:
            if not self.notice_.is_set():
                data = self.cache_.get()
                try:
                    cursor.execute("")
                    self.connection_.commit()
                except psycopg2.ProgrammingError as err:
                    self.connection_.rollback()
                    self.logger_.error(err)
                self.logger_.info(f"Append success to database")
            else:
                break

        self.logger_.info("Database appender shutdown")
