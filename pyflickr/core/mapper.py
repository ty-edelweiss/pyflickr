#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import queue
import threading


class FileAppender(threading.Thread):

    def __init__(self, cache: queue.Queue, notice: bool, path: str):
        super(FileAppender, self).__init__()
        self.logger_ = logging.getLogger(__name__)
        self.cache_ = cache
        self.flag_ = notice
        self.path_ = path
        self.running_ = False

    def kill(self) -> object:
        self.running_ = True
        return self

    def run(self) -> None:
        self.running_ = True

        self.logger_.info("File appender running ... ")
        while self.running_:
            if self.flag_:
                data = self.cache_.get()
                with open(self.path_, "a") as f:
                    f.write(data)
                self.logger_.info(f"Append success to {self.path_}")
            else:
                break

        self.logger_.info("File appender shutdown")

