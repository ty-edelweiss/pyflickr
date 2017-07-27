#!/usr/bin/env python
# -*- coding: utf-8 -*-

VENDER = "flickr"

if __name__ == "__main__":

    api = f"{VENDER}.photos.search"
    term = (
        "2016-1-1 00:00:00",
    )

    while True:
        params = manager()
        response = request.get(params)
        mapper.execute(response)
        time.sleep(1)
