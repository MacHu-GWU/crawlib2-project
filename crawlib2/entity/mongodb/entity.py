# -*- coding: utf-8 -*-

from typing import Dict, List
import mongoengine_mate
from mongoengine import fields, queryset

from . import query_builder
from ..base import Entity, ParseResult
from ...time_util import epoch
from ...status import Status


class MongodbEntity(mongoengine_mate.ExtendedDocument, Entity):
    meta = {
        "abstract": True,
    }

    @classmethod
    def get_unfinished(cls, filters=None):  # pragma: no cover
        """
        Execute a query to get all **Not Finished** web page ORM entity

        :type filters: dict
        :param filters: additional pymongo query dictionary syntax

        :rtype: queryset.QuerySet
        :return: a iterable ``mongoengine.queryset.QuerySet``
        """
        query_filters = query_builder.unfinished(
            finished_status=cls.CONF_FINISHED_STATUS,
            update_interval=cls.CONF_UPDATE_INTERVAL,
            status_key=cls.CONF_STATUS_KEY,
            edit_at_key=cls.CONF_EDIT_AT_KEY,
        )
        if (filters is not None) and isinstance(filters, dict):
            query_filters.update(filters)
        return cls.by_filter(query_filters)

    @classmethod
    def get_finished(cls, filters=None):  # pragma: no cover
        """
        Execute a query to get all **Finished** web page ORM entity

        :type filters: dict
        :param filters: additional pymongo query dictionary syntax

        :rtype: queryset.QuerySet
        :return: a iterable ``mongoengine.queryset.QuerySet``
        """
        query_filters = query_builder.finished(
            finished_status=cls.CONF_FINISHED_STATUS,
            update_interval=cls.CONF_UPDATE_INTERVAL,
            status_key=cls.CONF_STATUS_KEY,
            edit_at_key=cls.CONF_EDIT_AT_KEY,
        )
        if (filters is not None) and isinstance(filters, dict):
            query_filters.update(filters)
        return cls.by_filter(query_filters)

    @classmethod
    def validate_implementation_additional(cls):
        try:
            status_field = getattr(cls, cls.CONF_STATUS_KEY)
            if not isinstance(status_field, fields.IntField):
                raise NotImplementedError(
                    "edit at field has to be a `IntField` field!")
        except:
            raise NotImplementedError("status field (IntField) not found!")

        try:
            edit_at_field = getattr(cls, cls.CONF_EDIT_AT_KEY)
            if not isinstance(edit_at_field, fields.DateTimeField):
                raise NotImplementedError(
                    "edit at field has to be a `DateTimeField` field!")
        except:
            raise NotImplementedError(
                "edit at field (DateTimeField) not found!")

        for klass in cls.CONF_RELATIONSHIP.mapping:
            n_child_key = cls.CONF_RELATIONSHIP.get_n_child_key(klass)
            if hasattr(cls, n_child_key) is False:
                msg = "{} does not define '{}' field!".format(cls, n_child_key)
                raise NotImplementedError(msg)
            n_child_field = getattr(cls, n_child_key)
            if not isinstance(n_child_field, fields.IntField):
                raise NotImplementedError(
                    "`n_child` field has to be a `IntField` field!")

    def process_pr(self, pres, **kwargs):
        """
        Process ParseRequest

        :type pres: ParseResult
        :param pres:

        :return:
        """
        if pres.is_finished():
            # if pres.entity is not None:

            entity_bags = dict()  # type: Dict[MongodbEntity, List[MongodbEntity]]
            for child in pres.children:
                try:
                    entity_bags[child.__class__].append(child)
                except KeyError:
                    entity_bags[child.__class__] = [child, ]

            for entity_klass, entity_list in entity_bags.items():
                entity_klass.smart_insert(entity_list)
                n_child = len(entity_list)
                n_child_key = self.CONF_RELATIONSHIP.get_n_child_key(entity_klass)
                if pres.entity is not None:
                    setattr(pres.entity, n_child_key, n_child)

            if pres.entity is not None:
                setattr(pres.entity, self.id_field_name(), getattr(self, self.id_field_name()))
                setattr(pres.entity, self.CONF_STATUS_KEY, pres.status)
                setattr(pres.entity, self.CONF_EDIT_AT_KEY, pres.edit_at)
                self.smart_update(pres.entity)


class MongodbEntitySingleStatus(MongodbEntity):
    """

    **中文文档**

    如果某个页面的 Entity 类不会被其他类继承, 通常即意味着对于该页面我们只有一种抓取模式.
    也就是说只需要一套 ``status``, ``edit_at`` field.

    什么叫做: 会被其他类继承, 有多种抓取模式?

    例如, 我们要抓取一个图片网站上的图片. 网址的格式为 example.com/post/<post_id>

    1. 我们第一次访问 post 页面是抓取页面上的封面大图地址 (假设一个页面只有一张).
    2. 第二次访问 则是下载所有图片.

    我们通常是将 1, 2 分为两次操作, 以免图片下载失败就导致 post 页面也被标记为失败,
    导致要对页面重新访问. 造成重复操作.
    
    .. code-block:: python
    
        class Post(MongodbEntity):
            _id = fields.StringField(primary_key)
            status_detail = fields.IntField(default=0)
            edit_at_detail = fields.DateTimeField(default=epoch)
            cover_url = field.StringField()

            CONF_STATUS_KEY = "status_detail"
            CONF_EDIT_AT_KEY = "edit_at_detail"

            def build_url(self):
                return "www.example.com/post/{}".format(self._id)

        class PostCoverImage(Post)
            status_download = fields.IntField(default=0)
            edit_at_download = fields.DateTimeField(default=epoch)

            CONF_STATUS_KEY = "status_download"
            CONF_EDIT_AT_KEY = "edit_at_download"

            def build_url(self):
                return self.cover_url
    """

    meta = {
        "abstract": True,
    }

    CONF_STATUS_KEY = "status"
    CONF_EDIT_AT_KEY = "edit_at"

    status = fields.IntField(default=Status.S0_ToDo.id)
    edit_at = fields.DateTimeField(default=epoch)
