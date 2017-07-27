#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from typing import List, Any


class DateManager(object):

    def __init__(self, start: str, end: str = None, format: str = "%Y-%m-%d %H:%M:%S", delta: float = 86400.0):
        self.startDate_ = datetime.datetime.strptime(start, format)
        self.endDate_ = datetime.datetime.strptime(end, format) if end else datetime.datetime.now()
        self.currentDate_ = datetime.datetime.strptime(start, format)
        self.format_ = format
        self.d_ = delta - 1

    def __iter__(self):
        return self

    def __next__(self) -> datetime:
        currentDate = self.currentDate_
        nextDate = self.currentDate_ + datetime.timedelta(seconds=self.d_)
        if currentDate > self.endDate_:
            raise StopIteration()
        self.currentDate_ = nextDate + datetime.timedelta(seconds=1)
        return datetime.datetime.strftime(currentDate, self.format_), datetime.datetime.strftime(nextDate, self.format_)


class Validator(object):

    def __init__(self):
        self.status_ = "health"

    def check(self, subjects: Any) -> object:
        for subject in subjects:
            if subject:
                pass
            else:
                pass
        return self
