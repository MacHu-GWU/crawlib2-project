# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from crawlib2.entity.base import Relationship, RelationshipConfig, Entity, ParseResult


class TestRelationship(object):
    def test(self):
        class Post(object): pass

        with raises(TypeError):
            Relationship(Post, "many", "n_post")

        class Post(Entity): pass

        with raises(ValueError):
            Relationship(Post, "bad relationship value", "n_post")

        Relationship(Post, Relationship.Option.many, "n_post")


class TestRelationshipConfig(object):
    def test(self):
        class Post(Entity): pass

        config = RelationshipConfig([
            Relationship(Post, Relationship.Option.many, "n_post")
        ])
        assert config.get_relationship(Post) == Relationship.Option.many
        assert config.get_n_child_key(Post) == "n_post"


class TestEntity(object):
    def test_check_subclass_implementation_goodcase1(self):
        class Country(Entity):
            n_state = "n_state_field"

        class State(Entity):
            n_zipcode = "n_zipcode_field"

        class Zipcode(Entity): pass

        Country.CONF_RELATIONSHIP = RelationshipConfig([
            Relationship(State, Relationship.Option.many, "n_state"),
        ])

        State.CONF_RELATIONSHIP = RelationshipConfig([
            Relationship(Zipcode, Relationship.Option.many, "n_zipcode"),
        ])

        Entity.validate_relationship_config()

    def test_check_subclass_implementation_goodcase2(self):
        class ImagePage(Entity):
            id = "image_page_id"

        class ImageDownload(Entity):
            id = "image_page_id"

        ImagePage.CONF_RELATIONSHIP = RelationshipConfig([
            Relationship(ImageDownload, Relationship.Option.one, None),
        ])

        Entity.validate_relationship_config()


class TestParseResult(object):
    def test(self):
        pass


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
