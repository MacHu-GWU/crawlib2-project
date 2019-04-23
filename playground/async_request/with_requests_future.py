# -*- coding: utf-8 -*-

from urls import url_list
from requests_futures.sessions import FuturesSession
from sfm.timer import DateTimeTimer as Timer

ses = FuturesSession()

with Timer("with requests_future"):
    future_list = list()
    for url in url_list:
        future = ses.get(url)
        future_list.append(future)

    results = [len(future.result().text) for future in future_list]
    print(results)
