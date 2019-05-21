# -*- coding: utf-8 -*-

import pytest
from crawlib2.cache import create_cache_here
from crawlib2.cached_request import CachedRequest
from crawlib2.tests.dummy_site_crawler.site.s1_movie.entity_homepage import HomePage
from crawlib2.tests.dummy_site.movie.controller.view import max_page_id

cache = create_cache_here(__file__)
spider = CachedRequest(cache=cache, log_cache_miss=True, expire=24 * 3600)
spider.use_requests()


class TestHomePage(object):
    def test_parse_response(self):
        homepage = HomePage()
        url = homepage.build_url()
        html = spider.request_for_html(url)
        pres = homepage.parse_response(url, request=None, response=None, html=html)
        assert pres.entity.max_page_num == max_page_id
        assert len(pres.children) == max_page_id
        assert pres.children[-1] == max_page_id


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
