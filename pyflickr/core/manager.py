#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
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

    def __init__(self, contents: str = "photos.photo"):
        self.status_ = "health"
        self.target_ = contents

    def reset(self):
        self.status_ = "health"
        return self

    def deploy(self, text: str, format: str) -> object:
        obj = None
        if format == "json":
            obj = json.loads(text)
        return obj

    def check(self, response_text: str, format: str = "json") -> bool:
        subjects = self.deploy(response_text, format)
        for key in self.target_.split("."):
            if key in subjects:
                subjects = subjects[key]
                if not subjects:
                    self.status_ = "unhealth"
                    raise ValueError("target contents is empty")
                else:
                    continue
            else:
                self.status_ = "unhealth"
                raise ValueError("target contents key is not exist")
        return True
