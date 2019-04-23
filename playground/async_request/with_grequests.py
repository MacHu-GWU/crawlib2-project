# -*- coding: utf-8 -*-

"""
grequests 是 gevent + requests
"""

from urls import url_list
import grequests
from sfm.timer import DateTimeTimer as Timer

with Timer(title="use grequests"):
    req_list = [
        grequests.AsyncRequest(method="GET", url=url)
        for url in url_list
    ]
    res_list = grequests.map(req_list)
    results = [len(res.text) for res in res_list]
    print(results)
