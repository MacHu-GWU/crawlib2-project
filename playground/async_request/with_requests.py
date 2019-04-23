# -*- coding: utf-8 -*-

from urls import url_list
import requests
from sfm.timer import DateTimeTimer as Timer

with Timer(title="use requests"):
    results = list()
    for url in url_list:
        res = requests.get(url)
        results.append(len(res.text))
    print(results)
