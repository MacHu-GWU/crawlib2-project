# -*- coding: utf-8 -*-

import pytest
from crawlib2.cache import create_cache_here
from crawlib2.cached_request import CachedRequest
from crawlib2.tests.dummy_site_crawler.site.s2_music.entity_random_music import RandomMusicPage
from crawlib2.tests.dummy_site.music.controller.view import n_random_music

cache = create_cache_here(__file__)
spider = CachedRequest(cache=cache, log_cache_miss=True, expire=24 * 3600)
spider.use_requests()


class TestHomePage(object):
    def test_parse_response(self):
        rand_music_page = RandomMusicPage()
        url = rand_music_page.build_url()
        html = spider.request_for_html(url)
        pres = rand_music_page.parse_response(url, request=None, response=None, html=html)
        assert len(pres.entity.musics) == n_random_music
        assert len(pres.entity.musics) == len(pres.children)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
