# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from mongoengine import fields
from crawlib2.status import Status
from crawlib2.entity.base import Relationship, RelationshipConfig, ParseResult

from .url_builder import url_builder
from .entity_base import MovieWebsiteEntity
from .entity_movie import MoviePage
from ...config import Config


class ListPage(MovieWebsiteEntity):
    CONF_UPDATE_INTERVAL = 24 * 3600

    CONF_RELATIONSHIP = RelationshipConfig([
        Relationship(MoviePage, Relationship.Option.many, "n_movie")
    ])

    _id = fields.IntField(primary_key=True)
    n_movie = fields.IntField()

    meta = dict(
        collection="site_movie_listpage",
        db_alias=Config.MongoDB.database,
    )

    @property
    def page_num(self):
        return self._id

    def build_url(self):
        return url_builder.url_nth_listpage(self.page_num)

    def parse_response(self, url, request, response, html=None, **kwargs):
        if html is None:
            html = response.text

        soup = BeautifulSoup(html, "html.parser")
        div_listpage = soup.find("div", id="listpage")
        a_tag_list = div_listpage.find_all("a")

        entity = ListPage()

        children = list()
        for a in a_tag_list:
            href = a["href"]
            movie_id = int(href.split("/")[-1])
            movie = MoviePage(_id=movie_id)
            children.append(movie)

        status = Status.S50_Finished.id

        pres = ParseResult(
            entity=entity,
            children=children,
            data={},
            status=status,
        )
        return pres


ListPage.validate_implementation()
