# -*- coding: utf-8 -*-

"""

"""

from diskcache import Cache
from .decode import decoder

try:
    import requests
except ImportError:
    pass


class CachedRequest(object):
    """
    Implement a disk cache backed html puller, primarily using ``requests`` library.

    Usage:
    
    .. code-block:: python

        import pytest
        from crawlib2 import create_cache_here, CachedRequest
        from xxx import parse_html

        cache = create_cache_here(__file__)
        spider = CachedRequest(cache=cache)

        def test_parse_html_function():
            url = "https://www.python.org/downloads/"
            html = spider.request_for_html(url) # equivalent to requests.get(url)
            # validate your parse html function
            result = parse_html(html)

    To make post request:
    
    .. code-block:: python
    
        def test_parse_html_function():
            url = "https://www.python.org/downloads/"
            html = spider.request_for_html(
                url,
                request_method=requests.post,
                request_kwargs={"data": ...},
            )
            # validate your parse html function
            result = parse_html(html)


    **中文文档**

    在为爬虫程序写测试时, 由于我们要对 针对某一类 URL 所对应的 Html 进行数据抽取的函数
    进行测试, 我们希望在一段时间内, 比如1天内, 只爬取一次. 使得在本地机器上反复测试时,
    可以不用每次等待爬取. **以加快每次测试的速度**.
    """

    def __init__(self, cache, log_cache_miss=False, expire=24 * 3600):
        """
        :type cache: Cache
        :param cache:

        :type log_cache_miss: bool
        :param log_cache_miss: default False

        :type expire: int
        :param expire: default expire time for cache
        """
        if not isinstance(cache, Cache):
            raise TypeError
        self.cache = cache
        self.log_cache_miss = log_cache_miss
        self.expire = expire

        self.use_which = "requests"  # type: str
        self.get_html_method = self.get_html_method_for_requests  # type: callable
        self.use_requests()

    def use_requests(self):
        self.use_which = "requests"
        self.get_html_method = self.get_html_method_for_requests

    def get_html_method_for_requests(self,
                                     response,
                                     encoding=None,
                                     errors="strict",
                                     **kwargs):
        """
        Get html from ``requests.Response`` object.

        :type response: requests.Response
        :param response: the return of ``requests.request(method, url, **kwargs)``

        :type encoding: str
        :param encoding: manually specify the encoding.

        :type errors: str
        :param errors: errors handle method.

        :rtype: str
        :return: html
        """
        return decoder.decode(
            binary=response.content,
            url=response.url,
            encoding=encoding,
            errors=errors,
        )

    def request_for_html(self,
                         url,
                         get_html_method=None,
                         get_html_method_kwargs=None,
                         request_method=None,
                         request_kwargs=None,
                         cache_expire=None,
                         cacheable_callback=lambda html: True):
        """
        :type url: str
        :param url:

        :type get_html_method: callable
        :param get_html_method:

        :type get_html_method_kwargs: dict
        :param get_html_method_kwargs:

        :type request_method:
        :param request_method:

        :type request_kwargs: dict
        :param request_kwargs:

        :type cacheable_callback: callable
        :param cacheable_callback:

        :rtype: str
        """
        if get_html_method is None:
            get_html_method = self.get_html_method

        if get_html_method_kwargs is None:
            get_html_method_kwargs = dict()

        if request_method is None:
            request_method = requests.get

        if request_kwargs is None:
            request_kwargs = dict()

        if cache_expire is None:
            cache_expire = self.expire

        if self.use_which == "requests":
            if "url" not in request_kwargs:
                request_kwargs["url"] = url

        if url in self.cache:
            return self.cache[url]
        else:
            if self.log_cache_miss:
                msg = "{} doesn't hit cache!".format(url)
                print(msg)

            response = request_method(**request_kwargs)
            html = get_html_method(response, **get_html_method_kwargs)

            if cacheable_callback(html):
                self.cache.set(url, html, cache_expire)

            return html
