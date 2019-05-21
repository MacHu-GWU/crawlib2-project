# -*- coding: utf-8 -*-

from crawlib2.entity.base import Entity
from crawlib2.tests.dummy_site_crawler.db import client, db
from crawlib2.tests.dummy_site_crawler.site.s1_movie import (
    HomePage, ListPage, MoviePage
)
import requests

Entity.validate_relationship_config()

HomePage.smart_update(
    HomePage(_id=1, description="movie site homepage")
)

# for homepage in HomePage.get_unfinished():
#     url = homepage.build_url()
#     response = requests.get(url)
#     html = response.text
#     pres = homepage.parse_response(url, request=None, response=response, html=html)
#     homepage.process_pr(pres)


# for listpage in ListPage.objects():
#     print(listpage)


print(ListPage.objects.count())
print(MoviePage.objects.count())

HomePage.start_all()

print(ListPage.objects.count())
print(MoviePage.objects.count())