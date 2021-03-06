# -*- coding: utf-8 -*-

import pytest
from crawlib2.cache import create_cache_here
from crawlib2.cached_request import CachedRequest
from crawlib2.tests.dummy_site_crawler.site.s2_music.entity_music import MusicPage

cache = create_cache_here(__file__)
spider = CachedRequest(cache=cache, log_cache_miss=True, expire=24 * 3600)
spider.use_requests()


class TestMoviePage(object):
    def test_parse_response(self):
        music_id = 100
        music = MusicPage(_id=music_id)
        url = music.build_url()
        html = spider.request_for_html(url)
        pres = music.parse_response(url, request=None, response=None, html=html)
        assert pres.entity.title == "Music {} Title".format(music_id)
        assert len(pres.children) == 0


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
